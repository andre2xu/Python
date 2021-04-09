import sys, os, datetime, uuid, json
ROOT_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIRECTORY_PATH)

PFP_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY_PATH, 'static/images/pfp')
COVER_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY_PATH, 'static/images/cover')
GENERAL_FILES_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY_PATH, 'static/files')
IMAGE_FILES_DIRECTORY_PATH = os.path.join(ROOT_DIRECTORY_PATH, 'static/images/posts')

from flask import Flask, url_for, redirect, render_template, request, flash, send_file, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from PIL import Image
from forms import Login, Register, MyProfileSettings, MyAccountSettings, Clique2Post
from db import get_db, close_db, userAccountModel, userURLsModel, userClique1PostsModel, userClique1RatedPostsModel,  clique1_posts_file_upload_validator, userClique2PostsModel, clique2_posts_file_upload_validator, settings_upload_extension_validator, url_trimmer

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex # generates a random session key
app.permanent_session_lifetime = datetime.timedelta(days=1)



''' general routes & views '''

@app.route('/')
def index():
    login_form = Login()
    register_form = Register()

    return render_template('index.html', loginForm=login_form, registerForm=register_form)

@app.route('/choices/<url_username>', methods=['GET', 'POST'])
def clique_choices(url_username):
    '''
    The only people who can access this route are those who have already registered AND haven't chosen a clique yet. Unregistered visitors and registered users with cliques will be redirected to the index page to hint that they need to either sign up first or accept that they cannot change their cliques. The session variable 'verified_username_noclique' grants access to this route and it is only given to newly registered users when they fail the clique check in the login route (due to not having one).
    '''

    if 'verified_username_noclique' in session:
        db_connection = get_db()
        db_cursor = db_connection.cursor()

        if request.method == 'POST':
            if 'clique1' in request.form:
                db_cursor.execute(f'UPDATE accounts SET clique = ? WHERE username = ?', (request.form['clique1'], url_username))
                db_connection.commit() # gives user clique1

                session.pop('verified_username_noclique', None) # removes access to this route
                session['verified_username'] = url_username
                session['clique'] = request.form['clique1']

                return redirect(url_for('profile_page_clique1', url_username=url_username))

            if 'clique2' in request.form:
                db_cursor.execute(f'UPDATE accounts SET clique = ? WHERE username = ?', (request.form['clique2'], url_username))
                db_connection.commit() # gives user clique2

                session.pop('verified_username_noclique', None) # removes access to this route
                session['verified_username'] = url_username
                session['clique'] = request.form['clique2']

                return redirect(url_for('profile_page_clique2', url_username=url_username))

            if 'clique3' in request.form:
                print(request.form['clique3']) # unavailable

        return render_template('choices.html')

    else:
        return redirect(url_for('index'))

@app.route('/profile-clique1/<url_username>')
def profile_page_clique1(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # this prevents users from accessing their own accounts under a different clique (without this, they could easily manipulate their profile page layout by changing the clique specified in the URL)
    verify_clique = db_cursor.execute('SELECT COUNT(*) FROM accounts WHERE username = ? AND clique = "clique1"', (url_username,)).fetchone()

    if verify_clique[0] == 0:
        return redirect(url_for('index'))

    '''
    These two following checks take into account two different scenarios and provide protection against them: the first one prevents users with no accounts from accessing a registered user's profile page as an owner (this means they will not be able to make changes to it), the second check does the same thing as the first except this time it prevents other registered users from accessing a profile page as an owner; failure in either check will bring the user to a version of the target's profile page known as a 'view', where their actions are restricted.
    '''

    if 'verified_username' in session:
        if session['verified_username'] == url_username:
            full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
            userAccountData = userAccountModel(full_user_data)


            ''' WEBSITE URLs '''

            # this is used as a default if the user doesn't have any website URLs for their profile bio
            upbl_url_collection = []

            check_if_upbl_urls_exist = db_cursor.execute('SELECT COUNT(*) FROM urls WHERE username = ? AND clique = "clique1" AND role = "UPBL"', (url_username,)).fetchone() # UPBL means 'user profile bio link'

            # if the user has provided website URLs, they will be added to the list above one by one along with their complete database information
            if check_if_upbl_urls_exist[0] != 0:
                full_user_upbl_urls_data = db_cursor.execute('SELECT * FROM urls WHERE username = ? AND clique = "clique1" AND role = "UPBL"', (url_username,)).fetchall()

                for dataset in full_user_upbl_urls_data:
                    upbl_url_collection.append(userURLsModel(dataset))


            ''' POSTS '''

            # same as the website URLs part
            posts_collection = []

            check_if_posts_exist = db_cursor.execute('SELECT COUNT(*) FROM posts WHERE username = ? AND clique = ?', (url_username, 'clique1')).fetchone()

            if check_if_posts_exist[0] != 0:
                full_user_posts_data = db_cursor.execute('SELECT * FROM posts WHERE username = ? AND clique = ?', (url_username, 'clique1')).fetchall()

                for dataset in full_user_posts_data:
                    posts_collection.append(userClique1PostsModel(dataset))


            ''' FOLLOWERS '''

            followers_count = 0

            check_if_followers_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE user = ?', (url_username,)).fetchone()

            # if the user has followers, the total number of them will replace the default value initialized above
            if check_if_followers_exist[0] != 0:
                # this only counts the records that have the column 'is_following' set to 1. This prevents users, who have unfollowed, from being counted as a follower
                followers_count = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE user = ? AND is_following = 1', (url_username,)).fetchone()[0]


            ''' RATINGS '''

            # this is used as a default if the user doesn't have any ratings
            ratings_count = 0

            check_if_ratings_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_owner = ?', (url_username,)).fetchone()

            # same as the followers part
            if check_if_ratings_exist[0] != 0:
                ratings_count = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_owner = ? AND is_rated = 1', (url_username,)).fetchone()[0]

            return render_template('profile-page-clique1.html', userData=userAccountData, upblDataSet=upbl_url_collection, postsDataSet=posts_collection, followersCount=followers_count, ratingsCount=ratings_count)

        else:
            return redirect(url_for('profile_page_clique1_view', url_username=url_username))

    else:
        return redirect(url_for('profile_page_clique1_view', url_username=url_username))

@app.route('/profile-clique1-view/<url_username>')
def profile_page_clique1_view(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # see 'profile_page_clique1' to learn about this verification
    verify_clique = db_cursor.execute('SELECT COUNT(*) FROM accounts WHERE username = ? AND clique = "clique1"', (url_username,)).fetchone()

    if verify_clique[0] == 0:
        return redirect(url_for('index'))

    '''
    Views work the same way as their counterpart except for the fact that they allow anyone to access them. Please see 'profile_page_clique1' to learn about the various parts below
    '''

    full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
    userAccountData = userAccountModel(full_user_data)


    ''' WEBSITE URLs '''

    upbl_url_collection = []

    check_if_upbl_urls_exist = db_cursor.execute('SELECT COUNT(*) FROM urls WHERE username = ? AND clique = "clique1" AND role = "UPBL"', (url_username,)).fetchone()

    if check_if_upbl_urls_exist[0] != 0:
        full_user_upbl_urls_data = db_cursor.execute('SELECT * FROM urls WHERE username = ? AND clique = "clique1" AND role = "UPBL"', (url_username,)).fetchall()

        for dataset in full_user_upbl_urls_data:
            upbl_url_collection.append(userURLsModel(dataset))


    ''' POSTS '''

    posts_collection = []

    check_if_posts_exist = db_cursor.execute('SELECT COUNT(*) FROM posts WHERE username = ? AND clique = ?', (url_username, 'clique1')).fetchone()

    if check_if_posts_exist[0] != 0:
        full_user_posts_data = db_cursor.execute('SELECT * FROM posts WHERE username = ? AND clique = ?', (url_username, 'clique1')).fetchall()

        for dataset in full_user_posts_data:
            posts_collection.append(userClique1PostsModel(dataset))


    ''' FOLLOWERS '''

    followers_count = 0
    is_following = False;

    check_if_followers_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE user = ?', (url_username,)).fetchone()

    if check_if_followers_exist[0] != 0:
        followers_count = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE user = ? AND is_following = 1', (url_username,)).fetchone()[0]

        # this checks if the person viewing is following the user; if so, the follow button, which is the default, will be replaced by an unfollow button (THIS FEATURE ONLY APPEARS IN THE VIEW)
        if 'verified_username' in session:
            check_if_following = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE user = ? AND followed_by = ? AND is_following = 1', (url_username, session['verified_username'])).fetchone()

            if check_if_following[0] == 1:
                is_following = True


    ''' RATINGS '''

    ratings_count = 0
    rated_posts_id_collection = []

    check_if_ratings_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_owner = ?', (url_username,)).fetchone()

    if check_if_ratings_exist[0] != 0:
        ratings_count = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_owner = ? AND is_rated = 1', (url_username,)).fetchone()[0]

        # this checks for all the posts the viewer has rated (if any) and it fetches all their IDs which it stores in the list initialized above; these IDs determine which posts will have coloured stars (THIS FEATURE ONLY APPEARS IN THE VIEW)
        if 'verified_username' in session:
            check_if_viewer_rated_posts = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_owner = ? AND viewer = ? AND is_rated = 1', (url_username, session['verified_username'])).fetchone()

            if check_if_viewer_rated_posts[0] > 0:
                rated_posts_list = db_cursor.execute('SELECT post_id FROM clique1_ratings WHERE post_owner = ? AND viewer = ? AND is_rated = 1', (url_username, session['verified_username'])).fetchall()

                for post_id in rated_posts_list:
                    rated_posts_id_collection.append(post_id[0])

    return render_template('profile-page-clique1-view.html', userData=userAccountData, upblDataSet=upbl_url_collection, postsDataSet=posts_collection, followersCount=followers_count, isFollowing=is_following, ratingsCount=ratings_count, ratedPostsDataSet=rated_posts_id_collection)

@app.route('/profile-clique2/<url_username>')
def profile_page_clique2(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # see 'profile_page_clique1' to learn about this verification
    verify_clique = db_cursor.execute('SELECT COUNT(*) FROM accounts WHERE username = ? AND clique = "clique2"', (url_username,)).fetchone()

    if verify_clique[0] == 0:
        return redirect(url_for('index'))

    # see 'profile_page_clique1' to learn about the two following security checks & the various parts below

    if 'verified_username' in session:
        if session['verified_username'] == url_username:
            clique2post_form = Clique2Post()

            # initializing the flag that keeps the clique 2 post form active after a failed submission
            invalid_submission_flag = None

            if '_flashes' in session:
                invalid_submission_flag = True

            full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
            userAccountData = userAccountModel(full_user_data)


            ''' WEBSITE URLs '''

            upbl_url_collection = []

            check_if_upbl_urls_exist = db_cursor.execute('SELECT COUNT(*) FROM urls WHERE username = ? AND clique = "clique2" AND role = "UPBL"', (url_username,)).fetchone() # UPBL means 'user profile bio link'

            if check_if_upbl_urls_exist[0] != 0:
                full_user_upbl_urls_data = db_cursor.execute('SELECT * FROM urls WHERE username = ? AND clique = "clique2" AND role = "UPBL"', (url_username,)).fetchall()

                for dataset in full_user_upbl_urls_data:
                    upbl_url_collection.append(userURLsModel(dataset))


            ''' POSTS '''

            posts_collection = []

            check_if_posts_exist = db_cursor.execute('SELECT COUNT(*) FROM posts2 WHERE username = ? AND clique = "clique2"', (url_username,)).fetchone()

            if check_if_posts_exist[0] != 0:
                full_user_posts_data = db_cursor.execute('SELECT * FROM posts2 WHERE username = ? AND clique = "clique2"', (url_username,)).fetchall()

                for dataset in full_user_posts_data:
                    posts_collection.append(userClique2PostsModel(dataset))


            ''' FOLLOWERS '''

            followers_count = 0

            check_if_followers_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE user = ?', (url_username,)).fetchone()

            if check_if_followers_exist[0] != 0:
                followers_count = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE user = ? AND is_following = 1', (url_username,)).fetchone()[0]

            return render_template('profile-page-clique2.html', c2Form=clique2post_form, userData=userAccountData, upblDataSet=upbl_url_collection, postsDataSet=posts_collection, followersCount=followers_count, invalidSubmissionFlag=invalid_submission_flag)

        else:
            return redirect(url_for('profile_page_clique2_view', url_username=url_username))

    else:
        return redirect(url_for('profile_page_clique2_view', url_username=url_username))

@app.route('/profile-clique2-view/<url_username>')
def profile_page_clique2_view(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # see 'profile_page_clique1' to learn about this verification
    verify_clique = db_cursor.execute('SELECT COUNT(*) FROM accounts WHERE username = ? AND clique = "clique2"', (url_username,)).fetchone()

    if verify_clique[0] == 0:
        return redirect(url_for('index'))

    # see 'profile_page_clique1' to learn about the various parts below
    full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
    userAccountData = userAccountModel(full_user_data)


    ''' WEBSITE URLs '''

    upbl_url_collection = []

    check_if_upbl_urls_exist = db_cursor.execute('SELECT COUNT(*) FROM urls WHERE username = ? AND clique = "clique2" AND role = "UPBL"', (url_username,)).fetchone()

    if check_if_upbl_urls_exist[0] != 0:
        full_user_upbl_urls_data = db_cursor.execute('SELECT * FROM urls WHERE username = ? AND clique = "clique2" AND role = "UPBL"', (url_username,)).fetchall()

        for dataset in full_user_upbl_urls_data:
            upbl_url_collection.append(userURLsModel(dataset))


    ''' POSTS '''

    posts_collection = []

    check_if_posts_exist = db_cursor.execute('SELECT COUNT(*) FROM posts2 WHERE username = ? AND clique = "clique2"', (url_username,)).fetchone()

    if check_if_posts_exist[0] != 0:
        full_user_posts_data = db_cursor.execute('SELECT * FROM posts2 WHERE username = ? AND clique = "clique2"', (url_username,)).fetchall()

        for dataset in full_user_posts_data:
            posts_collection.append(userClique2PostsModel(dataset))


    ''' FOLLOWERS '''

    followers_count = 0
    is_following = False;

    check_if_followers_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE user = ?', (url_username,)).fetchone()

    if check_if_followers_exist[0] != 0:
        followers_count = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE user = ? AND is_following = 1', (url_username,)).fetchone()[0]

        if 'verified_username' in session:
            check_if_following = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE user = ? AND followed_by = ? AND is_following = 1', (url_username, session['verified_username'])).fetchone()

            if check_if_following[0] == 1:
                is_following = True


    ''' LIKES '''

    '''
    This operates similarly to the 'ratings' parts found in the two clique 1 functions, but the only difference is that this one doesn't need to get the total count of anything since the total number of likes a post has is stored in that post's record within the database. See the 'clique2_likes' table in the database schema.
    '''

    liked_posts_id_collection = []

    check_if_likes_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE post_owner = ?', (url_username,)).fetchone()

    if check_if_likes_exist[0] != 0:
        if 'verified_username' in session:
            check_if_viewer_liked_posts = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE post_owner = ? AND viewer = ? AND is_liked = 1', (url_username, session['verified_username'])).fetchone()

            if check_if_viewer_liked_posts[0] > 0:
                liked_posts_list = db_cursor.execute('SELECT post_id FROM clique2_likes WHERE post_owner = ? AND viewer = ? AND is_liked = 1', (url_username, session['verified_username'])).fetchall()

                for post_id in liked_posts_list:
                    liked_posts_id_collection.append(post_id[0])

    return render_template('profile-page-clique2-view.html', userData=userAccountData, upblDataSet=upbl_url_collection, postsDataSet=posts_collection, followersCount=followers_count, isFollowing=is_following, likedPostsDataSet=liked_posts_id_collection)

@app.route('/profile-settings-myprofile/<url_username>', methods=['GET', 'POST'])
def profile_settings_myprofile(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
    userAccountData = userAccountModel(full_user_data)

    # see 'profile_page_clique1' to learn about the two following security checks & the various parts below

    if 'verified_username' in session:
        if session['verified_username'] == url_username:
            myprofile_form = MyProfileSettings()

            # initializing wtforms inbuilt validator error messages for when form validation fails
            myprofile_name_error = None
            myprofile_bio_error = None


            if myprofile_form.validate_on_submit():

                '''
                The two empty dictionaries serve as a collective for ease of reference in the SQL queries below. Their key-value pairs, which are obtained from the dictionary updates, correspond to the column names and the column data. The keys are separated into their respective lists below, these are then iterated over in a for loop which lets the database cursor insert the inputs individually according to their column.
                '''

                non_empty_inputs = {}
                website_urls = {}

                # this handles the name and bio inputs
                if myprofile_form.name.data:
                    new_name = myprofile_form.name.data
                    non_empty_inputs.update({'name':new_name})
                if myprofile_form.bio.data:
                    new_bio = myprofile_form.bio.data
                    non_empty_inputs.update({'bio':new_bio})


                # this handles the selected niche input
                if 'niche' in request.form:
                    new_niche = request.form['niche']
                    
                    if new_niche == 'None':
                        non_empty_inputs.update({'niche':''})
                    else:
                        non_empty_inputs.update({'niche':new_niche})


                # this handles the website URL inputs
                if 'link0' in request.form:
                    new_link0 = request.form['link0']
                    processed_link0 = url_trimmer(new_link0)
                    website_urls.update({'link0':processed_link0})
                if 'link1' in request.form:
                    new_link1 = request.form['link1']
                    processed_link1 = url_trimmer(new_link1)
                    website_urls.update({'link1':processed_link1})
                if 'link2' in request.form:
                    new_link2 = request.form['link2']
                    processed_link2 = url_trimmer(new_link2)
                    website_urls.update({'link2':processed_link2})



                non_empty_inputs_keys = list(non_empty_inputs.keys())
                website_urls_keys = list(website_urls.keys())

                # updates accounts table
                for key in non_empty_inputs_keys:
                    db_cursor.execute(f'UPDATE accounts SET {key} = ? WHERE username = ?', (non_empty_inputs[key], url_username))
                    db_connection.commit()

                # updates URLs table
                for key in website_urls_keys:
                    role = 'UPBL'
                    db_cursor.execute('INSERT INTO urls (username, clique, role, url) VALUES (?,?,?,?)', (url_username, userAccountData['clique'], role, website_urls[key]))
                    db_connection.commit()

            # wtforms inbuilt validator error messages
            else:
                if 'name' in myprofile_form.errors:
                    myprofile_name_error = myprofile_form.errors['name'][0]
                
                if 'bio' in myprofile_form.errors:
                    myprofile_bio_error = myprofile_form.errors['bio'][0]

            return render_template('profile-settings-myprofile.html', userData=userAccountData, myprofileForm=myprofile_form, myprofileNameError=myprofile_name_error, myprofileBioError=myprofile_bio_error)

        else:
            return redirect(f'/profile-{userAccountData["clique"]}-view/{url_username}')

    else:
        return redirect(f'/profile-{userAccountData["clique"]}-view/{url_username}')

@app.route('/profile-settings-myaccount/<url_username>', methods=['GET', 'POST'])
def profile_settings_myaccount(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
    userAccountData = userAccountModel(full_user_data)

    # see 'profile_page_clique1' to learn about the two following security checks & the various parts below

    if 'verified_username' in session:
        if session['verified_username'] == url_username:
            myaccount_form = MyAccountSettings()

            # initializing wtforms inbuilt validator error messages for when form validation fails
            myaccount_newUsername_error = None
            myaccount_newPassword_error = None
            myaccount_confirmPassword_error = None


            if myaccount_form.validate_on_submit():
                # see 'profile_settings_myprofile' to learn about the system below
                non_empty_inputs = {}

                if myaccount_form.change_username.data:
                    new_username = myaccount_form.change_username.data
                    non_empty_inputs.update({'username':new_username})
                if myaccount_form.change_password.data:
                    new_password = myaccount_form.change_password.data
                    new_hashed_password = generate_password_hash(new_password)
                    non_empty_inputs.update({'password':new_hashed_password})

                non_empty_inputs_keys = list(non_empty_inputs.keys())

                for key in non_empty_inputs_keys:
                    db_cursor.execute(f'UPDATE accounts SET {key} = ? WHERE username = ?', (non_empty_inputs[key], url_username))
                    db_connection.commit()
                
                if 'username' in non_empty_inputs:
                    new_url_username = non_empty_inputs['username']
                    return redirect(f'/profile-settings-myaccount/{new_url_username}') # this redirection is ONLY used when the username has been changed
                else:
                    return redirect(f'/profile-settings-myaccount/{url_username}')

            # wtforms inbuilt validator error messages
            else:
                if 'change_username' in myaccount_form.errors:
                    myaccount_newUsername_error = myaccount_form.errors['change_username'][0]
                
                if 'change_password' in myaccount_form.errors:
                    myaccount_newPassword_error = myaccount_form.errors['change_password'][0]

                if 'confirm_password' in myaccount_form.errors:
                    myaccount_confirmPassword_error = myaccount_form.errors['confirm_password'][0]

            return render_template('profile-settings-myaccount.html', userData=userAccountData, myaccountForm=myaccount_form, myaccountNewUsernameError=myaccount_newUsername_error, myaccountNewPasswordError=myaccount_newPassword_error, myaccountConfirmPasswordError=myaccount_confirmPassword_error)

        else:
            return redirect(f'/profile-{userAccountData["clique"]}-view/{url_username}')

    else:
        return redirect(f'/profile-{userAccountData["clique"]}-view/{url_username}')

@app.route('/profile-clique1/file_viewer/<url_filename>')
def clique1_file_viewer(url_filename):
    return send_file(os.path.join(GENERAL_FILES_DIRECTORY_PATH + f'/{url_filename}'), cache_timeout=0)



''' login/register forms '''

@app.route('/login', methods=['POST'])
def login():
    login_form = Login()
    register_form = Register()

    # initializing wtforms inbuilt validator error messages for when form validation fails
    login_username_error = None
    login_password_error = None


    if login_form.validate_on_submit():
        login_username = login_form.usernameLog.data
        login_password = login_form.passwordLog.data

        db_connection = get_db()
        db_cursor = db_connection.cursor()

        full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (login_username,)).fetchall()

        # this checks if the user exists
        if full_user_data:
            check_password = check_password_hash(full_user_data[0][1], login_password)

            if check_password:
                userAccountData = userAccountModel(full_user_data)

                '''
                If the user has successfully authenticated but doesn't have a clique yet, then they will be taken to the route where they can choose one, otherwise, they will be brought to their profile page.
                '''

                if userAccountData['clique'] is not None:
                    session['verified_username'] = login_username
                    session['clique'] = userAccountData['clique']
                    return redirect(f'/profile-{userAccountData["clique"]}/{userAccountData["username"]}')
                
                else:
                    session['verified_username_noclique'] = login_username
                    return redirect(url_for('clique_choices', url_username=userAccountData['username']))

            else:
                flash("Invalid username or password", 'invalidCredentials')
                return redirect(url_for('index'))

        else:
            flash("Invalid username or password", 'invalidCredentials')
            return redirect(url_for('index'))

    else:
        # wtforms inbuilt validator error messages
        if 'usernameLog' in login_form.errors:
            login_username_error = login_form.errors['usernameLog'][0]

        if 'passwordLog' in login_form.errors:
            login_password_error = login_form.errors['passwordLog'][0]

    return render_template('index.html', loginForm=login_form, registerForm=register_form, loginUsernameError=login_username_error, loginPasswordError=login_password_error)


@app.route('/register', methods=['POST'])
def register():
    login_form = Login()
    register_form = Register()

    # initializing wtforms inbuilt validator error messages for when form validation fails
    register_username_error = None
    register_password_error = None

    # initializing the flag that keeps the register form active after a failed submission
    invalid_submission_flag = None


    if register_form.validate_on_submit():
        register_username = register_form.usernameReg.data
        register_password = register_form.passwordReg.data

        db_connection = get_db()
        db_cursor = db_connection.cursor()

        full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (register_username,)).fetchall()

        # this checks if the username provided is already taken
        if not(full_user_data):
            hashed_password = generate_password_hash(register_password)
            register_date = datetime.datetime.utcnow().strftime('%d/%m/%Y')

            db_cursor.execute('INSERT INTO accounts (username, password, joined) VALUES (?,?,?)', (register_username, hashed_password, register_date))
            db_connection.commit()

            return redirect(url_for('index'))

        else:
            flash("That username is already taken", 'invalidUsername')
            return render_template('index.html', loginForm=login_form, registerForm=register_form, invalidSubmissionFlag=True) # even though the form submission was valid here, the flag is still set to true in order to prevent the register form from disppearing so that it can display the error message

    # wtforms inbuilt validator error messages
    else:
        if 'usernameReg' in register_form.errors:
            register_username_error = register_form.errors['usernameReg'][0]
        
        if 'passwordReg' in register_form.errors:
            register_password_error = register_form.errors['passwordReg'][0]

        return render_template('index.html', loginForm=login_form, registerForm=register_form, registerUsernameError=register_username_error, registerPasswordError=register_password_error, invalidSubmissionFlag=True)

    return render_template('index.html', loginForm=login_form, registerForm=register_form)



''' upload routes '''

@app.route('/profile-clique1/<url_username>/post-upload', methods=['POST'])
def clique1_post_upload(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    '''
    The system below is similar to the one implemented in 'profile_settings_myprofile', but this time, it allows empty inputs to be added to the collective and the dictionary isn't converted into a list to be iterated over. The collective is used entirely in the SQL insertion rather than column-by-column (i.e. key-by-key) like before.
    '''

    non_empty_inputs = {}

    # this handles the post's title
    if request.form['post_title']:
        post_title = request.form['post_title']
        non_empty_inputs.update({'title':post_title})
    else:
        non_empty_inputs.update({'title':''})


    # this handles the post's body
    if request.form['post_body']:
        post_body = request.form['post_body']
        non_empty_inputs.update({'body':post_body})
    else:
        non_empty_inputs.update({'body':''})


    # this handles any files attached to the post
    if request.files['post_body_file']:
        post_file = request.files['post_body_file']
        post_file_filename = secure_filename(post_file.filename)
        post_file_extension = post_file_filename.split('.')[1]
        validation_result, file_type = clique1_posts_file_upload_validator(post_file_extension)

        if validation_result:
            if file_type == 'img':
                new_post_filename = str(uuid.uuid4()) + f'.{post_file_extension}'

                unprocessed_image = Image.open(post_file)
                unprocessed_width = unprocessed_image.size[0]
                unprocessed_height = unprocessed_image.size[1]

                # initializing dimensions
                processed_width = unprocessed_width
                processed_height = unprocessed_height

                # width must be greater than height for resizing to occur!
                if unprocessed_width > 800 and unprocessed_height < (unprocessed_width * 0.6):
                    processed_width = unprocessed_width - (unprocessed_width * 0.6)

                if unprocessed_height > 800 and unprocessed_width > (unprocessed_height * 0.6):
                    processed_height = unprocessed_height - (unprocessed_height * 0.6)

                processed_image = unprocessed_image.resize((int(processed_width), int(processed_height)))
                processed_image.save(os.path.join(IMAGE_FILES_DIRECTORY_PATH, new_post_filename))
                non_empty_inputs.update({'file':new_post_filename, 'file_type':'img'})

            elif file_type == 'other':
                new_post_filename = str(uuid.uuid4()) + f'.{post_file_extension}'
                post_file.save(os.path.join(GENERAL_FILES_DIRECTORY_PATH, new_post_filename))
                non_empty_inputs.update({'file':new_post_filename, 'file_type':'other'})
            
        else:
            print("File upload was invalid.")
            non_empty_inputs.update({'file':'', 'file_type':''})
    
    else:
        non_empty_inputs.update({'file':'', 'file_type':''})



    post_title_upload = non_empty_inputs['title']
    post_body_upload = non_empty_inputs['body']
    post_file_upload = non_empty_inputs['file']
    post_file_type_upload = non_empty_inputs['file_type']

    # the insertion only occurs when the post isn't completely empty
    if post_title_upload != None and post_body_upload != None and post_file_upload != None and post_file_type_upload != None:
        post_id = str(uuid.uuid4())
        db_cursor.execute('INSERT INTO posts (id, username, clique, title, body, file, file_type) VALUES (?,?,?,?,?,?,?)', (post_id, url_username, 'clique1', post_title_upload, post_body_upload, post_file_upload, post_file_type_upload))
        db_connection.commit()

    return redirect(url_for('profile_page_clique1', url_username=url_username))

@app.route('/profile-clique2/<url_username>/post-upload', methods=['POST'])
def clique2_post_upload(url_username):
    clique2_post_form = Clique2Post()

    # initializing wtforms inbuilt validator error messages for when form validation fails
    caption_error = None

    if clique2_post_form.validate_on_submit():
        db_connection = get_db()
        db_cursor = db_connection.cursor()

        # the clique is used in the SQL insertion below
        check_clique = db_cursor.execute('SELECT clique FROM accounts WHERE username = ?', (url_username,)).fetchone()[0]

        # this checks if the user has made at least one post (used later...)
        check_if_posts_exist = db_cursor.execute('SELECT COUNT(*) FROM posts2 WHERE username = ?', (url_username,)).fetchone()

        post_content = request.files['post_pic_or_vid']
        post_caption = clique2_post_form.caption.data

        post_content_filename = secure_filename(post_content.filename)
        post_content_extension = post_content_filename.split('.')[1]
        validation_result, file_type = clique2_posts_file_upload_validator(post_content_extension) # validates the extension of the picture/video the user has uploaded and determines whether the content is one or the other

        if validation_result:
            # if the content is a picture, it will be resized first before it is uploaded to the server
            if file_type == 'img':
                post_id = str(uuid.uuid4())
                post_timestamp = datetime.datetime.utcnow() # this timestamp is used for retrieving the 'colgroup' of the most recent post
                new_post_content_filename = str(uuid.uuid4()) + f'.{post_content_extension}'

                '''
                The if-else statement below handles the arrangement of the user's posts. The posts in clique 2 are laid out in 3 columns:
                
                I wanted the user to first fill out an entire row before moving onto the next one (i.e. occupy a spot in all 3 columns before moving down the feed), so what I did was I assigned a group, labelled with the numbers 1 to 3, to each of the three columns. Each post will be assigned a group number which depends on the value of the previous one, so if the previous one was in colgroup 1, the next post will be in colgroup 2, etc. This is done by retrieving the group number of the most recent post and incrementing it; only the group numbers 1 and 2 are incremented, if the latest post has a value of 3 then the next post will be assigned colgroup 1. Refer to the code below for easier understanding...
                '''

                if check_if_posts_exist[0] != 0:
                    check_colgroup_of_latest_post = db_cursor.execute('SELECT colgroup FROM posts2 WHERE username = ? ORDER BY timestamp DESC LIMIT 1', (url_username,)).fetchone()[0]

                    # this is only assigned when the recent post's colgroup is 3
                    current_post_colgroup = 1

                    if check_colgroup_of_latest_post == 1 or check_colgroup_of_latest_post == 2:
                        current_post_colgroup = check_colgroup_of_latest_post + 1

                    db_cursor.execute('INSERT INTO posts2 (id, username, clique, colgroup, caption, file, file_type, timestamp, likes) VALUES (?,?,?,?,?,?,?,?, 0)', (post_id, url_username, check_clique, current_post_colgroup, post_caption, new_post_content_filename, file_type, post_timestamp))
                    db_connection.commit()

                # this segment is only triggered when the user doesn't have any posts yet; it assigns the colgroup 1 to the first post
                else:
                    db_cursor.execute('INSERT INTO posts2 (id, username, clique, colgroup, caption, file, file_type, timestamp, likes) VALUES (?,?,?,?,?,?,?,?, 0)', (post_id, url_username, check_clique, 1, post_caption, new_post_content_filename, file_type, post_timestamp))
                    db_connection.commit()

                original_post_content = Image.open(post_content)
                new_post_content = original_post_content.resize((500, 400))
                new_post_content.save(os.path.join(IMAGE_FILES_DIRECTORY_PATH, new_post_content_filename))


            # if the content is a video, it's file size is left as it is and it is immediately uploaded to the server
            if file_type == 'vid':
                post_id = str(uuid.uuid4())
                post_timestamp = datetime.datetime.utcnow()
                new_post_content_filename = str(uuid.uuid4()) + f'.{post_content_extension}'

                # same grouping system as above is applied here
                if check_if_posts_exist[0] != 0:
                    check_colgroup_of_latest_post = db_cursor.execute('SELECT colgroup FROM posts2 WHERE username = ? ORDER BY timestamp DESC LIMIT 1', (url_username,)).fetchone()[0]

                    current_post_colgroup = 1

                    if check_colgroup_of_latest_post == 1 or check_colgroup_of_latest_post == 2:
                        current_post_colgroup = check_colgroup_of_latest_post + 1

                    db_cursor.execute('INSERT INTO posts2 (id, username, clique, colgroup, caption, file, file_type, timestamp, likes) VALUES (?,?,?,?,?,?,?,?, 0)', (post_id, url_username, check_clique, current_post_colgroup, post_caption, new_post_content_filename, file_type, post_timestamp))
                    db_connection.commit()

                else:
                    db_cursor.execute('INSERT INTO posts2 (id, username, clique, colgroup, caption, file, file_type, timestamp, likes) VALUES (?,?,?,?,?,?,?,?, 0)', (post_id, url_username, check_clique, 1, post_caption, new_post_content_filename, file_type, post_timestamp))
                    db_connection.commit()

                post_content.save(os.path.join(GENERAL_FILES_DIRECTORY_PATH, new_post_content_filename))

    # wtforms inbuilt validator error message
    else:
        if 'caption' in clique2_post_form.errors:
            caption_error = clique2_post_form.errors['caption'][0]
            flash(caption_error, 'invalidCaption')

    return redirect(url_for('profile_page_clique2', url_username=url_username))

@app.route('/profile-settings-myprofile/<url_username>/upload', methods=['POST'])
def pfp_cover_upload(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
    userAccountData = userAccountModel(full_user_data)

    ''' 
    Any file that is sent here undergoes three processing stages before it is uploaded to the server: 

    (STAGE 1)
    The file's extension is passed into a custom extension validator that returns a boolean value depending on whether the extension was valid or not. This helps to prevent potentially malicious files from being uploaded to the server.

    (STAGE 2)  
    If the extension is valid, the process continues and, depending on which image is being updated, the old pfp/cover file is deleted from its respective directory and its filename is also removed from the database; this is done before any changes are made so that the server's memory is used more efficiently.

    (STAGE 3)
    After the cleanup (if any occurred), the file is given a new name in the form of a UUID to ensure that it doesn't overwrite any existing files that could have had the same name and which may or may not have been owned by the user. It is then resized to the proper dimensions to reduce its file size and it's new filename is stored in the database for later reference, and lastly, the newly resized file itself is stored in its respective directory.
    '''

    if 'pfp' in request.files:
        pfp_upload = request.files['pfp']
        pfp_upload_filename = secure_filename(pfp_upload.filename)
        
        pfp_upload_extension = pfp_upload_filename.split('.')[1]
        extension_validator_result = settings_upload_extension_validator(pfp_upload_extension)

        if extension_validator_result:
            # this checks for and deletes the existing profile picture owned by the user
            old_pfp = userAccountData['pfp']
            if old_pfp:
                os.remove(os.path.join(PFP_DIRECTORY_PATH, old_pfp))
                db_cursor.execute('UPDATE accounts SET pfp = NULL WHERE username = ?', (url_username,))
                db_connection.commit()

            # first the new pfp filename is created and uploaded to the database, and THEN the new pfp is uploaded to the server
            new_pfp_filename = str(uuid.uuid4()) + f'.{pfp_upload_extension}'
            db_cursor.execute('UPDATE accounts SET pfp = ? WHERE username = ?', (new_pfp_filename, url_username))
            db_connection.commit()

            original_pfp = Image.open(pfp_upload)
            new_pfp = original_pfp.resize((200, 200))
            new_pfp.save(os.path.join(PFP_DIRECTORY_PATH, new_pfp_filename))


    if 'cover' in request.files:
        cover_upload = request.files['cover']
        cover_upload_filename = secure_filename(cover_upload.filename)
        
        cover_upload_extension = cover_upload_filename.split('.')[1]
        extension_validator_result = settings_upload_extension_validator(cover_upload_extension)

        if extension_validator_result:
            # this checks for and deletes the existing cover owned by the user
            old_cover = userAccountData['cover']
            if old_cover:
                os.remove(os.path.join(COVER_DIRECTORY_PATH, old_cover))
                db_cursor.execute('UPDATE accounts SET cover = NULL WHERE username = ?', (url_username,))
                db_connection.commit()

            # first the new cover filename is created and uploaded to the database, and THEN the new cover is uploaded to the server
            new_cover_filename = str(uuid.uuid4()) + f'.{cover_upload_extension}'
            db_cursor.execute('UPDATE accounts SET cover = ? WHERE username = ?', (new_cover_filename, url_username))
            db_connection.commit()

            original_cover = Image.open(cover_upload)
            new_cover = original_cover.resize((1500, 400))
            new_cover.save(os.path.join(COVER_DIRECTORY_PATH, new_cover_filename))

    return redirect(url_for('profile_settings_myprofile', url_username=url_username))

@app.route('/profile-clique1-view/<url_username>/being-followed-by-<viewer>')
def clique1_follows(url_username, viewer):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    '''
    The system below takes into account two scenarios: 

    (1) This is the first time the viewer is following this user so a new record of them will be inserted.

    (2) The viewer had previously unfollowed this user and is now following them again, so their existing record is updated instead of a new one being inserted.
    '''

    check_if_follower_exists = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE user = ? AND followed_by = ?', (url_username, viewer)).fetchone()


    # first time following
    if check_if_follower_exists[0] == 0:
        viewer_clique = db_cursor.execute('SELECT clique FROM accounts WHERE username = ?', (viewer,)).fetchone()

        db_cursor.execute('INSERT INTO clique1_followers (user, followed_by, follower_clique, is_following) VALUES (?,?,?,?)', (url_username, viewer, viewer_clique[0], 1))
        db_connection.commit()


    # following again
    else:
        check_if_not_following_anymore = db_cursor.execute('SELECT is_following FROM clique1_followers WHERE user = ? AND followed_by = ?', (url_username, viewer)).fetchone()

        if check_if_not_following_anymore[0] == 0:
            db_cursor.execute('UPDATE clique1_followers SET is_following = 1 WHERE user = ? AND followed_by = ?', (url_username, viewer))
            db_connection.commit()

    return redirect(url_for('profile_page_clique1_view', url_username=url_username))

@app.route('/profile-clique1-view/<url_username>/<viewer>-rates-<url_id>')
def clique1_ratings(url_username, viewer, url_id):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    '''
    The system below takes into account two scenarios: 

    (1) This is the first time the viewer is rating this post so a new record of them will be inserted.

    (2) The viewer had previously unrated this post but is now rating it again, so their existing record will be updated instead of a new one being inserted.
    '''

    check_if_rating_exists = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_id = ? AND viewer = ?', (url_id, viewer)).fetchone()

    is_rated = 0

    # first time rating
    if check_if_rating_exists[0] == 0:
        db_cursor.execute('INSERT INTO clique1_ratings (post_owner, post_id, viewer, is_rated) VALUES (?,?,?,?)', (url_username, url_id, viewer, 1))
        db_connection.commit()
        is_rated = 1


    # unrating or rating again
    else:
        check_if_rated_already = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_id = ? AND viewer = ? AND is_rated = 1', (url_id, viewer)).fetchone()

        if check_if_rated_already[0] == 1:
            db_cursor.execute('UPDATE clique1_ratings SET is_rated = 0 WHERE post_id = ? AND viewer = ?', (url_id, viewer))
            db_connection.commit()
            is_rated = 0

        elif check_if_rated_already[0] == 0:
            db_cursor.execute('UPDATE clique1_ratings SET is_rated = 1 WHERE post_id = ? AND viewer = ?', (url_id, viewer))
            db_connection.commit()
            is_rated = 1

    return jsonify(is_rated)

@app.route('/profile-clique2-view/<url_username>/being-followed-by-<viewer>')
def clique2_follows(url_username, viewer):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # see 'clique1_follows' to learn about the followers system below

    check_if_follower_exists = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE user = ? AND followed_by = ?', (url_username, viewer)).fetchone()


    # first time following
    if check_if_follower_exists[0] == 0:
        viewer_clique = db_cursor.execute('SELECT clique FROM accounts WHERE username = ?', (viewer,)).fetchone()

        db_cursor.execute('INSERT INTO clique2_followers (user, followed_by, follower_clique, is_following) VALUES (?,?,?,?)', (url_username, viewer, viewer_clique[0], 1))
        db_connection.commit()


    # following again
    else:
        check_if_not_following_anymore = db_cursor.execute('SELECT is_following FROM clique2_followers WHERE user = ? AND followed_by = ?', (url_username, viewer)).fetchone()

        if check_if_not_following_anymore[0] == 0:
            db_cursor.execute('UPDATE clique2_followers SET is_following = 1 WHERE user = ? AND followed_by = ?', (url_username, viewer))
            db_connection.commit()

    return redirect(url_for('profile_page_clique2_view', url_username=url_username))

@app.route('/profile-clique2-view/<url_username>/<viewer>-likes-<url_id>')
def clique2_likes(url_username, viewer, url_id):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # this system is similar to the one used in 'clique1_ratings' except it updates the total number of likes in a post whenever a user likes/unlikes it

    check_if_likes_exists = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE post_id = ? AND viewer = ?', (url_id, viewer)).fetchone()

    is_liked = 0

    # first time liking
    if check_if_likes_exists[0] == 0:
        db_cursor.execute('INSERT INTO clique2_likes (post_owner, post_id, viewer, is_liked) VALUES (?,?,?,?)', (url_username, url_id, viewer, 1))
        db_connection.commit()
        is_liked = 1

        old_likes_count = db_cursor.execute('SELECT likes FROM posts2 WHERE id = ?', (url_id,)).fetchone()[0]
        new_likes_count = old_likes_count + 1
        db_cursor.execute('UPDATE posts2 SET likes = ? WHERE id = ?', (new_likes_count, url_id))
        db_connection.commit()


    # unliking or liking again
    else:
        check_if_liked_already = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE post_id = ? AND viewer = ? AND is_liked = 1', (url_id, viewer)).fetchone()

        if check_if_liked_already[0] == 1:
            db_cursor.execute('UPDATE clique2_likes SET is_liked = 0 WHERE post_id = ? AND viewer = ?', (url_id, viewer))
            db_connection.commit()
            is_liked = 0

            old_likes_count = db_cursor.execute('SELECT likes FROM posts2 WHERE id = ?', (url_id,)).fetchone()[0]
            new_likes_count = old_likes_count - 1
            db_cursor.execute('UPDATE posts2 SET likes = ? WHERE id = ?', (new_likes_count, url_id))
            db_connection.commit()

        elif check_if_liked_already[0] == 0:
            db_cursor.execute('UPDATE clique2_likes SET is_liked = 1 WHERE post_id = ? AND viewer = ?', (url_id, viewer))
            db_connection.commit()
            is_liked = 1

            old_likes_count = db_cursor.execute('SELECT likes FROM posts2 WHERE id = ?', (url_id,)).fetchone()[0]
            new_likes_count = old_likes_count + 1
            db_cursor.execute('UPDATE posts2 SET likes = ? WHERE id = ?', (new_likes_count, url_id))
            db_connection.commit()

    return jsonify(is_liked)

@app.route('/profile-search-clique1', methods=['POST'])
def profile_search_clique1():
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    '''
    The if statement portion is only triggered when the user submits their search query rather than using the suggestion list. It first checks to see whether the username they entered exists in the database, and if so, they will be taken to a view of that user's profile page. However, if they entered an invalid username, they will either be redirected back to their own profile page (if they have logged in) or the home page (if they have no account or have not logged in yet).

    The parts that aren't encased in the if statement are for the user suggestion list. It obtains data from the JS scripts found in the profile page templates - JQuery's AJAX is used to make this work without form submission. Whenever the user is lifting their finger from the keyboard after typing, a request is sent to Flask containing the letter(s) they've entered in the searchbar. This is used to query usernames in the database containing such letters and the result of that query is then sent back to the same JS script to be appended as an 'li' node in the user suggestion list.

    The reason for the multiple search processing routes is because I plan to make the different cliques return user suggestions based on features that's unique to them: for example, I want the clique 1 search system to put user's who have higher ratings at the top of the suggestion list (I haven't implemented this feature yet***).
    '''

    if 'clique1-searchbar' in request.form:
        target_username = request.form['clique1-searchbar']

        check_if_target_exists = db_cursor.execute('SELECT COUNT(*) FROM accounts WHERE username = ?', (target_username,)).fetchone()

        if check_if_target_exists[0] != 0:
            url_clique = db_cursor.execute('SELECT clique FROM accounts WHERE username = ?', (target_username,)).fetchone()
            return redirect(f'/profile-{url_clique[0]}-view/{target_username}')

        else:
            if 'verified_username' in session:
                url_clique = db_cursor.execute('SELECT clique FROM accounts WHERE username = ?', (session['verified_username'],)).fetchone()
                return redirect(f'/profile-{url_clique[0]}/{session["verified_username"]}')
            else:
                return redirect(url_for('index'))

    search_query = request.json['search_query']

    search_results = db_cursor.execute('SELECT username, clique FROM accounts WHERE username LIKE ? AND clique IS NOT NULL', (f'%{search_query}%',)).fetchall()

    return json.dumps(search_results)

@app.route('/profile-search-clique2', methods=['POST'])
def profile_search_clique2():
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # see 'profile_search_clique1' to learn about how the search system works & my reason for using different routes

    if 'clique2-searchbar' in request.form:
        target_username = request.form['clique2-searchbar']

        check_if_target_exists = db_cursor.execute('SELECT COUNT(*) FROM accounts WHERE username = ?', (target_username,)).fetchone()

        if check_if_target_exists[0] != 0:
            url_clique = db_cursor.execute('SELECT clique FROM accounts WHERE username = ?', (target_username,)).fetchone()
            return redirect(f'/profile-{url_clique[0]}-view/{target_username}')

        else:
            if 'verified_username' in session:
                url_clique = db_cursor.execute('SELECT clique FROM accounts WHERE username = ?', (session['verified_username'],)).fetchone()
                return redirect(f'/profile-{url_clique[0]}/{session["verified_username"]}')
            else:
                return redirect(url_for('index'))

    search_query = request.json['search_query']

    search_results = db_cursor.execute('SELECT username, clique FROM accounts WHERE username LIKE ? AND clique IS NOT NULL', (f'%{search_query}%',)).fetchall()

    return json.dumps(search_results)



''' deletion routes '''

@app.route('/profile-clique1/<url_username>/post-delete-<url_id>')
def clique1_post_delete(url_username, url_id):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    clique1_post_data = db_cursor.execute('SELECT * FROM posts WHERE id = ?', (url_id,)).fetchone()

    # these two checks will delete the file, that's attached on the post, from the server
    if clique1_post_data[5] and clique1_post_data[6] == 'img':
        os.remove(os.path.join(IMAGE_FILES_DIRECTORY_PATH + f'/{clique1_post_data[5]}'))

    elif clique1_post_data[5] and clique1_post_data[6] == 'other':
        os.remove(os.path.join(GENERAL_FILES_DIRECTORY_PATH + f'/{clique1_post_data[5]}'))

    db_cursor.execute('DELETE FROM posts WHERE id = ? AND username = ?', (url_id, url_username))
    db_connection.commit()

    # this deletes any record of the post in the clique 1 ratings table
    check_if_ratings_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_id = ?', (url_id,)).fetchone()

    if check_if_ratings_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique1_ratings WHERE post_id = ?', (url_id,))
        db_connection.commit()

    return redirect(url_for('profile_page_clique1', url_username=url_username))

@app.route('/profile-clique1/delete-account-<url_username>')
def clique1_account_delete(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    '''
    The checks below determine whether the user has any website URL, posts, or pfp/cover tied to their account, and if so, they will be removed from the server BEFORE the account itself is deleted. This ensures that memory is not wasted on files that won't be used by anybody anymore.
    '''

    # this handles the deletion of website URLs
    check_if_urls_exist = db_cursor.execute('SELECT COUNT(*) FROM urls WHERE username = ?', (url_username,)).fetchone()
    if check_if_urls_exist[0] != 0:
        db_cursor.execute('DELETE FROM urls WHERE username = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of posts
    check_if_posts_with_attachments_exist = db_cursor.execute('SELECT COUNT(file) FROM posts WHERE username = ? AND file <> ""', (url_username,)).fetchone()
    check_if_posts_without_attachments_exist = db_cursor.execute('SELECT COUNT(file) FROM posts WHERE username = ? AND file = ""', (url_username,)).fetchone()

    if check_if_posts_with_attachments_exist[0] != 0:
        files_list = db_cursor.execute('SELECT file, file_type FROM posts WHERE username = ? AND file <> ""', (url_username,)).fetchall()

        # deletes attached files
        for file in files_list:
            if file[1] == 'img':
                os.remove(os.path.join(IMAGE_FILES_DIRECTORY_PATH + f'/{file[0]}'))
            elif file[1] == 'other':
                os.remove(os.path.join(GENERAL_FILES_DIRECTORY_PATH + f'/{file[0]}'))

        db_cursor.execute('DELETE FROM posts WHERE username = ?', (url_username,))
        db_connection.commit()

    if check_if_posts_without_attachments_exist[0] != 0:
        db_cursor.execute('DELETE FROM posts WHERE username = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of followers & following
    check_if_followers_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE user = ?', (url_username,)).fetchone()
    check_if_following_anybody = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE followed_by = ?', (url_username,)).fetchone()
    check_if_following_anybody2 = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE followed_by = ?', (url_username,)).fetchone()

    if check_if_followers_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique1_followers WHERE user = ?', (url_username,))
        db_connection.commit()
    
    if check_if_following_anybody[0] != 0:
        db_cursor.execute('DELETE FROM clique1_followers WHERE followed_by = ?', (url_username,))
        db_connection.commit()
    
    if check_if_following_anybody2[0] != 0:
        db_cursor.execute('DELETE FROM clique2_followers WHERE followed_by = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of ratings
    check_if_ratings_given_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE viewer = ?', (url_username,)).fetchone()
    check_if_ratings_received_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE post_owner = ?', (url_username,)).fetchone()

    if check_if_ratings_given_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique1_ratings WHERE viewer = ?', (url_username,))
        db_connection.commit()

    if check_if_ratings_received_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique1_ratings WHERE post_owner = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of any likes given to clique 2 users
    check_if_likes_given_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE viewer = ?', (url_username,)).fetchone()

    if check_if_likes_given_exist[0] != 0:
        all_liked_posts_id = db_cursor.execute('SELECT post_id FROM clique2_likes WHERE viewer = ?', (url_username,)).fetchall()

        for post_id in all_liked_posts_id:
            old_likes_count = db_cursor.execute('SELECT likes FROM posts2 WHERE id = ?', (post_id[0],)).fetchone()[0]
            new_likes_count = old_likes_count - 1
            db_cursor.execute('UPDATE posts2 SET likes = ? WHERE id = ?', (new_likes_count, post_id[0]))

        db_cursor.execute('DELETE FROM clique2_likes WHERE viewer = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of the pfp & cover
    check_if_pfp_exists = db_cursor.execute('SELECT COUNT(pfp) FROM accounts WHERE username = ?', (url_username,)).fetchone()
    check_if_cover_exists = db_cursor.execute('SELECT COUNT(cover) FROM accounts WHERE username = ?', (url_username,)).fetchone()

    if check_if_pfp_exists[0] != 0:
        pfp_filename = db_cursor.execute('SELECT pfp FROM accounts WHERE username = ?', (url_username,)).fetchone()
        os.remove(os.path.join(PFP_DIRECTORY_PATH + f'/{pfp_filename[0]}'))
        db_cursor.execute('UPDATE accounts SET pfp = NULL WHERE username = ?', (url_username,))
        db_connection.commit()

    if check_if_cover_exists[0] != 0:
        cover_filename = db_cursor.execute('SELECT cover FROM accounts WHERE username = ?', (url_username,)).fetchone()
        os.remove(os.path.join(COVER_DIRECTORY_PATH + f'/{cover_filename[0]}'))
        db_cursor.execute('UPDATE accounts SET cover = NULL WHERE username = ?', (url_username,))
        db_connection.commit()


    db_cursor.execute('DELETE FROM accounts WHERE username = ?', (url_username,))
    db_connection.commit()
    return redirect(url_for('index'))

@app.route('/profile-clique2/<url_username>/post-delete-<url_id>')
def clique2_post_delete(url_username, url_id):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    clique2_post_data = db_cursor.execute('SELECT * FROM posts2 WHERE id = ?', (url_id,)).fetchone()

    # these two checks will delete the file, that's attached on the post, from the server
    if clique2_post_data[6] == 'img':
        os.remove(os.path.join(IMAGE_FILES_DIRECTORY_PATH + f'/{clique2_post_data[5]}'))

    elif clique2_post_data[6] == 'vid':
        os.remove(os.path.join(GENERAL_FILES_DIRECTORY_PATH + f'/{clique2_post_data[5]}'))

    db_cursor.execute('DELETE FROM posts2 WHERE id = ? AND username = ?', (url_id, url_username))
    db_connection.commit()

    # this deletes any record of the post in the clique 2 likes table
    check_if_likes_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE post_id = ?', (url_id,)).fetchone()

    if check_if_likes_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique2_likes WHERE post_id = ?', (url_id,))
        db_connection.commit()

    return redirect(url_for('profile_page_clique2', url_username=url_username))

@app.route('/profile-clique2/delete-account-<url_username>')
def clique2_account_delete(url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    # see 'clique1_account_delete' to learn about the checks below

    # this handles the deletion of website URLs
    check_if_urls_exist = db_cursor.execute('SELECT COUNT(*) FROM urls WHERE username = ?', (url_username,)).fetchone()
    if check_if_urls_exist[0] != 0:
        db_cursor.execute('DELETE FROM urls WHERE username = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of posts
    check_if_image_posts_exists = db_cursor.execute('SELECT COUNT(*) FROM posts2 WHERE username = ? AND file_type = "img"', (url_username,)).fetchone()
    check_if_video_posts_exists = db_cursor.execute('SELECT COUNT(*) FROM posts2 WHERE username = ? AND file_type = "vid"', (url_username,)).fetchone()

    if check_if_image_posts_exists[0] != 0:
        image_posts_filename_collection = db_cursor.execute('SELECT file FROM posts2 WHERE username = ? AND file_type = "img"', (url_username,)).fetchall()

        for image_filename in image_posts_filename_collection:
            os.remove(os.path.join(IMAGE_FILES_DIRECTORY_PATH, image_filename[0]))

    if check_if_video_posts_exists[0] != 0:
        video_posts_filename_collection = db_cursor.execute('SELECT file FROM posts2 WHERE username = ? AND file_type = "vid"', (url_username,)).fetchall()

        for video_filename in video_posts_filename_collection:
            os.remove(os.path.join(GENERAL_FILES_DIRECTORY_PATH, video_filename[0]))

    db_cursor.execute('DELETE FROM posts2 WHERE username = ?', (url_username,))
    db_connection.commit()


    # this handles the deletion of followers & following
    check_if_followers_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE user = ?', (url_username,)).fetchone()
    check_if_following_anybody = db_cursor.execute('SELECT COUNT(*) FROM clique2_followers WHERE followed_by = ?', (url_username,)).fetchone()
    check_if_following_anybody2 = db_cursor.execute('SELECT COUNT(*) FROM clique1_followers WHERE followed_by = ?', (url_username,)).fetchone()

    if check_if_followers_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique2_followers WHERE user = ?', (url_username,))
        db_connection.commit()
    
    if check_if_following_anybody[0] != 0:
        db_cursor.execute('DELETE FROM clique2_followers WHERE followed_by = ?', (url_username,))
        db_connection.commit()

    if check_if_following_anybody2[0] != 0:
        db_cursor.execute('DELETE FROM clique1_followers WHERE followed_by = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of likes
    check_if_likes_given_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE viewer = ?', (url_username,)).fetchone()
    check_if_likes_received_exist = db_cursor.execute('SELECT COUNT(*) FROM clique2_likes WHERE post_owner = ?', (url_username,)).fetchone()

    if check_if_likes_given_exist[0] != 0:
        all_liked_posts_id = db_cursor.execute('SELECT post_id FROM clique2_likes WHERE viewer = ?', (url_username,)).fetchall()

        for post_id in all_liked_posts_id:
            old_likes_count = db_cursor.execute('SELECT likes FROM posts2 WHERE id = ?', (post_id[0],)).fetchone()[0]
            new_likes_count = old_likes_count - 1
            db_cursor.execute('UPDATE posts2 SET likes = ? WHERE id = ?', (new_likes_count, post_id[0]))

        db_cursor.execute('DELETE FROM clique2_likes WHERE viewer = ?', (url_username,))
        db_connection.commit()

    if check_if_likes_received_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique2_likes WHERE post_owner = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of any ratings given to clique 1 users
    check_if_ratings_given_exist = db_cursor.execute('SELECT COUNT(*) FROM clique1_ratings WHERE viewer = ?', (url_username,)).fetchone()

    if check_if_ratings_given_exist[0] != 0:
        db_cursor.execute('DELETE FROM clique1_ratings WHERE viewer = ?', (url_username,))
        db_connection.commit()


    # this handles the deletion of the pfp & cover
    check_if_pfp_exists = db_cursor.execute('SELECT COUNT(pfp) FROM accounts WHERE username = ?', (url_username,)).fetchone()
    check_if_cover_exists = db_cursor.execute('SELECT COUNT(cover) FROM accounts WHERE username = ?', (url_username,)).fetchone()

    if check_if_pfp_exists[0] != 0:
        pfp_filename = db_cursor.execute('SELECT pfp FROM accounts WHERE username = ?', (url_username,)).fetchone()
        os.remove(os.path.join(PFP_DIRECTORY_PATH + f'/{pfp_filename[0]}'))
        db_cursor.execute('UPDATE accounts SET pfp = NULL WHERE username = ?', (url_username,))
        db_connection.commit()

    if check_if_cover_exists[0] != 0:
        cover_filename = db_cursor.execute('SELECT cover FROM accounts WHERE username = ?', (url_username,)).fetchone()
        os.remove(os.path.join(COVER_DIRECTORY_PATH + f'/{cover_filename[0]}'))
        db_cursor.execute('UPDATE accounts SET cover = NULL WHERE username = ?', (url_username,))
        db_connection.commit()


    db_cursor.execute('DELETE FROM accounts WHERE username = ?', (url_username,))
    db_connection.commit()
    return redirect(url_for('index'))

@app.route('/profile-settings-myprofile/delete-<url_target>-of-<url_username>')
def delete_settings_upload(url_target, url_username):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    '''
    This deletion uses the name of the file (a.k.a 'url_target') to specify whether to delete the user's profile picture or their cover. It does this by comparing the filename, that was passed from the href attribute, with the filenames of the user's profile picture and cover.
    '''

    full_user_data = db_cursor.execute('SELECT * FROM accounts WHERE username = ?', (url_username,)).fetchall()
    userAccountData = userAccountModel(full_user_data)

    if url_target == userAccountData['pfp']:
        os.remove(os.path.join(PFP_DIRECTORY_PATH, url_target))
        db_cursor.execute('UPDATE accounts SET pfp = NULL WHERE username = ?', (url_username,))
        db_connection.commit()
    
    if url_target == userAccountData['cover']:
        os.remove(os.path.join(COVER_DIRECTORY_PATH, url_target))
        db_cursor.execute('UPDATE accounts SET cover = NULL WHERE username = ?', (url_username,))
        db_connection.commit()

    return redirect(url_for('profile_settings_myprofile', url_username=url_username))

@app.route('/profile-clique1-view/<url_username>/unfollowed-by-<current_follower>')
def clique1_unfollows(url_username, current_follower):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    db_cursor.execute('UPDATE clique1_followers SET is_following = 0 WHERE user = ? AND followed_by = ?', (url_username, current_follower))
    db_connection.commit()

    return redirect(url_for('profile_page_clique1_view', url_username=url_username))

@app.route('/profile-clique2-view/<url_username>/unfollowed-by-<current_follower>')
def clique2_unfollows(url_username, current_follower):
    db_connection = get_db()
    db_cursor = db_connection.cursor()

    db_cursor.execute('UPDATE clique2_followers SET is_following = 0 WHERE user = ? AND followed_by = ?', (url_username, current_follower))
    db_connection.commit()

    return redirect(url_for('profile_page_clique2_view', url_username=url_username))



''' error handlers '''

@app.errorhandler(BadRequest)
def handle_badrequest(error):
    return redirect(url_for('index'))

@app.errorhandler(NotFound)
def handle_notfound(error):
    return redirect(url_for('index'))

@app.errorhandler(InternalServerError)
def handle_internalservererror(error):
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('verified_username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
import sys, os, uuid, datetime

sys.path.append(os.path.dirname(__file__)) # allows the use of custom modules within the directory
sys.path.append(os.path.dirname(__file__) + '/venv/Lib/site-packages') # connects the path of the root directory (i.e. Flask-Profile) with the module directory and appends the resulting path into the list of pathnames (i.e. sys.path) where Python looks for modules (YOU MAY HAVE TO CHANGE THE STRING PART OF THE PATH IF YOU ARE NOT USING A VIRTUAL ENVIRONMENT)

from flask import Flask, flash, session, render_template, url_for, make_response, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, NotFound
from flask_pymongo import PyMongo
from forms import LoginForm, RegisterForm, ProfileChanges, AccountChanges, PasswordChanges, BlogPost

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex
app.permanent_session_lifetime = datetime.timedelta(days=3)
app.config['UPLOAD_FOLDER'] = os.path.dirname(__file__) + '/static/images/uploads'


''' database connection & configuration '''

mongodb = PyMongo(app, uri='mongodb+srv://test-admin:1234@practice.lo3nq.mongodb.net/testdb?retryWrites=true&w=majority')
db_collection = mongodb.db.accounts # establishes direct connection to accounts collection
db_blogs_collection = mongodb.db.blogs # establishes direct connection to blogs collection


''' views & routes '''

# homepage
@app.route('/')
def homepage():
    return render_template('index.html')

# profile page
@app.route('/user/profile/<url_username>')
def profile_page(url_username):
    if 'verified_email' in session:
        full_user_data = db_collection.find_one({'username':f'{url_username}'})
        full_user_blog_data = db_blogs_collection.find({'username':f'{url_username}'}) # needs to be looped over to retrieve individual blogs

        if session['verified_email'] == full_user_data['email']: # prevents access to anyone else's account
            blog_post = BlogPost()
            return render_template('profile-page.html', userData=full_user_data, userBlog=blog_post, userBlogData=full_user_blog_data)
        else:
            return redirect(url_for('login'))
    
    else:
        return redirect(url_for('homepage'))

# profile page settings
@app.route('/user/profile/<url_username>/account')
def profile_settings(url_username):
    if 'verified_email' in session:
        full_user_data = db_collection.find_one({'username':f'{url_username}'})

        if session['verified_email'] == full_user_data['email']: # prevents access to anyone else's account
            profile_changes = ProfileChanges()
            account_changes = AccountChanges()
            password_changes = PasswordChanges()

            return render_template('profile-settings.html', userData=full_user_data, profileChangesForm=profile_changes, accountChangesForm=account_changes, passwordChangesForm=password_changes)
        else:
            return redirect(url_for('login'))

    else:
        return redirect(url_for('homepage'))


''' profile page forms '''

# blog posts
@app.route('/user/profile/<url_username>/blog-post', methods=['POST'])
def blog_post(url_username):
    blog_post = BlogPost()

    if blog_post.validate_on_submit():
        blog_title = blog_post.blog_title.data
        blog_body = blog_post.blog_body.data

        blog_post_date = datetime.datetime.now().strftime('%d/%m/%Y') # this is displayed on the blog itself
        post_timestamp = datetime.datetime.now() # prevents blogs from being overwritten by another blog that was posted on the same day

        check_timestamp = db_blogs_collection.find_one({'timestamp':f'{post_timestamp}'})

        if not(check_timestamp):
            db_blogs_collection.insert_one({'username':f'{url_username}', 'timestamp':f'{post_timestamp}', 'title':f'{blog_title}', 'body':f'{blog_body}', 'date':f'{blog_post_date}'})

    # error messages for failed validation
    if 'blog_title' in blog_post.errors:
        flash(str(blog_post.errors['blog_title'][0]), 'blogTitleError')
    if 'blog_body' in blog_post.errors:
        flash(str(blog_post.errors['blog_body'][0]), 'blogBodyError')

    return redirect(f'/user/profile/{url_username}')

# profile changes
@app.route('/user/profile/<url_username>/account/profile-changes', methods=['POST'])
def profile_changes(url_username):
    profile_changes = ProfileChanges()

    if profile_changes.validate_on_submit():
        new_name = profile_changes.change_name.data
        new_bio = profile_changes.change_bio.data

        if new_name and not(new_bio):
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'name':f'{new_name}'}}, upsert=False)
        if new_bio and not(new_name):
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'bio':f'{new_bio}'}}, upsert=False)
        if new_name and new_bio:
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'name':f'{new_name}','bio':f'{new_bio}'}}, upsert=False)
    
    # error message for failed validation
    if 'change_bio' in profile_changes.errors:
        flash(str(profile_changes.errors['change_bio'][0]), 'bioError')
    
    return redirect(f'/user/profile/{url_username}/account')

# account changes
@app.route('/user/profile/<url_username>/account/account-changes', methods=['POST'])
def account_changes(url_username):
    account_changes = AccountChanges()

    if account_changes.validate_on_submit():
        new_email = account_changes.change_email.data
        new_username = account_changes.change_username.data

        if new_email and not(new_username):
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'email':f'{new_email}'}}, upsert=False)
            full_user_data = db_collection.find_one({'username':f'{url_username}'})
            temporary_username = full_user_data['username']
            return redirect(f'/user/profile/{temporary_username}/account')
        
        if new_username and not(new_email):
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'username':f'{new_username}'}}, upsert=False)
            return redirect(f'/user/profile/{new_username}/account')
        
        if new_email and new_username:
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'email':f'{new_email}', 'username':f'{new_username}'}}, upsert=False)
            return redirect(f'/user/profile/{new_username}/account')
    
    # error message for failed validation
    if 'change_email' in account_changes.errors:
        flash(str(account_changes.errors['change_email'][0]), 'settingsEmailError')
    
    return redirect(f'/user/profile/{url_username}/account')

# password changes
@app.route('/user/profile/<url_username>/account/security-changes', methods=['POST'])
def security_changes(url_username):
    password_changes = PasswordChanges()

    if password_changes.validate_on_submit():
        new_password = password_changes.change_password.data
        new_hashed_password = generate_password_hash(new_password)

        db_collection.update_many({'username':f'{url_username}'}, {'$set': {'password':f'{new_hashed_password}'}}, upsert=False)
    
    # error message for failed validation
    if 'change_password' in password_changes.errors:
        flash(str(password_changes.errors['change_password'][0]), 'settingsPasswordError')
    
    return redirect(f'/user/profile/{url_username}/account')

# image uploads
@app.route('/user/profile/<url_username>/account/upload', methods=['POST'])
def uploads(url_username):
    pfp_file = request.files['pfp']
    cover_file = request.files['cover']

    full_user_data = db_collection.find_one({'username':f'{url_username}'})
    check_pfp = full_user_data['pfp'] # indicates the presence/absence of a custom profile pic in the database (empty means absence)
    check_cover = full_user_data['cover'] # indicates the presence/absence of a custom background cover in the database (empty means absence)

    ''' the if-else statements below will do two separate checks: first to see whether the user wants to change their profile picture or background cover or both, and the second is to see whether they already have image files inside the server's images directory; if they do then the file or files will be deleted first before their pfp/cover is updated. The purpose of the two 'check' variables above is that they return the filename(s), from the database, of the pfp/cover that is stored in the server's own images directory; of course an empty string means that the user does not have that file in the server '''

    if pfp_file and not(cover_file):
        if not(check_pfp):
            secured_pfp_filename = secure_filename(pfp_file.filename)
            pfp_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_pfp_filename))
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'pfp':f'{secured_pfp_filename}'}}, upsert=False)
        else:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], check_pfp))
            secured_pfp_filename = secure_filename(pfp_file.filename)
            pfp_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_pfp_filename))
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'pfp':f'{secured_pfp_filename}'}}, upsert=False)
    
    
    if cover_file and not(pfp_file):
        if not(check_cover):
            secured_cover_filename = secure_filename(cover_file.filename)
            cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_cover_filename))
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'cover':f'{secured_cover_filename}'}}, upsert=False)
        else:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], check_cover))
            secured_cover_filename = secure_filename(cover_file.filename)
            cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_cover_filename))
            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'cover':f'{secured_cover_filename}'}}, upsert=False)
    
    
    if pfp_file and cover_file:
        if not(check_pfp) and not(check_cover):
            secured_pfp_filename = secure_filename(pfp_file.filename)
            secured_cover_filename = secure_filename(cover_file.filename)

            pfp_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_pfp_filename))
            cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_cover_filename))

            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'pfp':f'{secured_pfp_filename}', 'cover':f'{secured_cover_filename}'}}, upsert=False)
        else:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], check_pfp))
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], check_cover))

            secured_pfp_filename = secure_filename(pfp_file.filename)
            secured_cover_filename = secure_filename(cover_file.filename)

            pfp_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_pfp_filename))
            cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_cover_filename))

            db_collection.update_many({'username':f'{url_username}'}, {'$set': {'pfp':f'{secured_pfp_filename}', 'cover':f'{secured_cover_filename}'}}, upsert=False)

    return redirect(f'/user/profile/{url_username}/account')


''' login & register forms '''

# register page & form authentication
@app.route('/user/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit() and request.method == 'POST':
        form_email = request.form['email']
        form_username = request.form['username']
        form_password = request.form['password']
        
        if not(db_collection.find_one({'email':f'{form_email}'})):
            if not(db_collection.find_one({'username':f'{form_username}'})):
                
                hashed_password = generate_password_hash(form_password)
                user_join_date = datetime.datetime.now().strftime('%Y-%m-%d')

                db_collection.insert_one({'email':f'{form_email}', 'username':f'{form_username}', 'password':f'{hashed_password}', 'date':f'{user_join_date}', 'pfp':'', 'cover':'', 'name':'', 'bio':''})

                return redirect(url_for('login'))
            else:
                flash("That username is already taken", 'invalidUsername')
                return redirect(url_for('register'))
        else:
            flash("That email address is already in use", 'invalidEmail')
            return redirect(url_for('register'))

    ''' the if-else statements below look for error messages in the WTForms errors dictionary; error messages are only assigned to their respective keys when a validator condition in the form model fails or isn't met by the user's input. THIS SECTION CAN ONLY BE FIRED IF THE FORM VALIDATION FAILS '''

    if 'email' in register_form.errors:
        email_error_message = register_form.errors['email'][0]
    else:
        email_error_message = None
    
    if 'username' in register_form.errors:
        username_error_message = register_form.errors['username'][0]
    else:
        username_error_message = None
    
    if 'password' in register_form.errors:
        password_error_message = register_form.errors['password'][0]
    else:
        password_error_message = None

    return render_template('register.html', registerForm=register_form, emailError=email_error_message, usernameError=username_error_message, passwordError=password_error_message)


# login page & form authentication
@app.route('/user/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if 'verified_email' in session and 'verified_username' in session:
        session_username = session['verified_username']
        return redirect(f'/user/profile/{session_username}')
    
    else:
        if login_form.validate_on_submit() and request.method == 'POST':
            form_email = request.form['email']
            form_username = request.form['username']
            form_password = request.form['password']

            full_user_data = db_collection.find_one({'email':f'{form_email}'})

            if not(full_user_data):
                flash("Sorry but that email address is incorrect", 'invalidEmail')
                return redirect(url_for('login'))
            else:
                if not(full_user_data['username'] == form_username):
                    flash("Incorrect username", 'invalidUsername')
                    return redirect(url_for('login'))
                else:
                    password_comparison = check_password_hash(full_user_data['password'], form_password)

                    if not(password_comparison):
                        flash("Incorrect password", 'invalidPassword')
                        return redirect(url_for('login'))
                    else:
                        session['verified_email'] = full_user_data['email']
                        session['verified_username'] = full_user_data['username']

                        session.permanent = True # activates permanent session timer

                        return redirect(f'/user/profile/{form_username}')

    ''' the if-else statements below look for error messages in the WTForms errors dictionary; error messages are only assigned to their respective keys when a validator condition in the form model fails or isn't met by the user's input. THIS SECTION CAN ONLY BE FIRED IF THE FORM VALIDATION FAILS '''

    if 'email' in login_form.errors:
        email_error_message = login_form.errors['email'][0]
    else:
        email_error_message = None
    
    if 'username' in login_form.errors:
        username_error_message = login_form.errors['username'][0]
    else:
        username_error_message = None
    
    if 'password' in login_form.errors:
        password_error_message = login_form.errors['password'][0]
    else:
        password_error_message = None

    return render_template('login.html', loginForm=login_form, emailError=email_error_message, usernameError=username_error_message, passwordError=password_error_message)

# terminates session & redirects user back to homepage
@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys()) if key != '_flashes'] # deletes anything stored in the session that isn't a flash message
    return redirect(url_for('homepage'))


''' error handlers '''

@app.errorhandler(NotFound)
def error_notfound(error):
    print("Not Found error caught.")
    return redirect(url_for('homepage'))

@app.errorhandler(BadRequest)
def error_badrequest(error):
    print("Bad request error caught.")
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=True)

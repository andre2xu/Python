import sys, uuid, datetime, os
sys.path.append('c:/Users/andre/Documents/Python/Flask-Profile/venv/Lib/site-packages') # MUST CHANGE FOR PRODUCTION

from flask import Flask, flash, redirect, request, render_template, url_for, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import length, Optional, InputRequired

app = Flask(__name__)

app.secret_key = uuid.uuid4().hex #generates a random unique ID for sessions
app.permanent_session_lifetime = datetime.timedelta(days=3)

app.config['UPLOAD_FOLDER'] = 'c:/Users/andre/Documents/Python/Flask-Profile/static/images' # MUST CHANGE FOR PRODUCTION

# MongoDB Atlas connection
app.config['MONGO_URI'] = 'mongodb+srv://test-admin:1234@practice.lo3nq.mongodb.net/testdb?retryWrites=true&w=majority'
mydb = PyMongo(app)

db_collection = mydb.db.accounts #direct connection to mongo collection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/register')
def register():
    return render_template('register.html')

@app.route('/user/login')
def login():

    # if the user's credentials are already stored in the cookies then they are used for automatic authentication with the database (the cookies only last up to 2 mins)
    if 'stored_username' in request.cookies:
        cookies_email = request.cookies.get('stored_email')
        cookies_username = request.cookies.get('stored_username')
        cookies_password = request.cookies.get('stored_password')

        # DB QUERY (retrieves user's information from database for comparison)
        db_full_data = db_collection.find_one({"email":f"{cookies_email}"})

        # the user's database info is compared with the user's cookies info
        if not(db_full_data):
            return redirect(url_for('login'))
        elif db_full_data:
            if cookies_username != db_full_data['username']:
                return redirect(url_for('login'))
            elif cookies_username == db_full_data['username']:  
                if cookies_password != db_full_data['password']:
                    return redirect(url_for('login'))
                elif cookies_password == db_full_data['password']:
                    session['verified'] = True
                    return profile_redirect(db_full_data["username"])

    # otherwise the user will have to sign in manually
    else:
        return render_template('login.html')

# redirects user to profile page URL containing their username
@app.route('/user/profile')
def profile_redirect(db_username):
    return redirect(f'/user/profile/{db_username}')

# user profile page
@app.route('/user/profile/<url_username>')
def profile_page(url_username):

    if 'verified' in session:
        # DB QUERY (retrieves user's full data for later use in their profile page)
        user_db_data = db_collection.find_one({"username":f"{url_username}"})

        return render_template('profile-page.html', account_name=url_username, userData=user_db_data)
    else:
        return redirect(url_for('login'))



# --- PROFILE PAGE SETTINGS FORM (uses Flask-WTF) ---
class ChangeSettings(FlaskForm):
    name = StringField('Name', validators=[Optional(), length(min=1, max=25)])
    age = StringField('Age', validators=[Optional(), length(min=1, max=2)])
    gender = StringField('Gender', validators=[Optional()])

@app.route('/user/profile/<url_username>/account', methods=['GET', 'POST'])
def account_settings(url_username):
    myform = ChangeSettings()

    # if the changes for the account meet the criteria for a valid submission (see validators above for the criteria) then the inputs are retrieved and passed through a series of if conditions to see what needs to be updated in the database
    if myform.validate_on_submit():
        form_name = myform.name.data
        form_age = myform.age.data
        form_gender = myform.gender.data

        if not(form_name) and form_age and form_gender:
            db_collection.update_many({"username":f"{url_username}"}, {"$set": {"age":f"{form_age}", "gender":f"{form_gender}"}}, upsert=False)        
        
        elif not(form_age) and form_name and form_gender:
            db_collection.update_many({"username":f"{url_username}"}, {"$set": {"name":f"{form_name}", "gender":f"{form_gender}"}}, upsert=False)
        
        elif not(form_gender) and form_name and form_age:
            db_collection.update_many({"username":f"{url_username}"}, {"$set": {"name":f"{form_name}", "age":f"{form_age}"}}, upsert=False)
        
        elif form_name and form_age and form_gender:
            db_collection.update_many({"username":f"{url_username}"}, {"$set": {"name":f"{form_name}", "age":f"{form_age}", "gender":f"{form_gender}"}}, upsert=False)

        elif form_name and not(form_age) and not(form_gender):
            db_collection.update_many({"username":f"{url_username}"}, {"$set": {"name":f"{form_name}"}}, upsert=False)

        elif not(form_name) and form_age and not(form_gender):
            db_collection.update_many({"username":f"{url_username}"}, {"$set": {"age":f"{form_age}"}}, upsert=False)

        elif not(form_name) and not(form_age) and form_gender:
            db_collection.update_many({"username":f"{url_username}"}, {"$set": {"gender":f"{form_gender}"}}, upsert=False)
        
        elif not(form_name) and not(form_age) and not(form_gender):
            print("You need to enter values in order to update!")

        # user is redirected back to their profile page after the changes have been made
        return profile_redirect(url_username)

    # this if statement prevents users who aren't logged in from accessing someone's or their account indirectly through the settings page URL
    if 'verified' in session:
        # DB QUERY (retrieves user's full data for later use in their profile settings page)
        user_db_data = db_collection.find_one({"username":f"{url_username}"})

        return render_template('profile-settings.html', account_name=url_username, settingsForm=myform, userData=user_db_data)
    else:
        return redirect(url_for('login'))

# profile picture processing
@app.route('/user/profile/<url_username>/account/upload', methods=['POST'])
def pfp_upload(url_username):
    user_db_data = db_collection.find_one({"username":f"{url_username}"})

    user_pic = request.files['pfp']
    secured_pic_filename = secure_filename(user_pic.filename)

    # saves the uploaded picture to local images directory
    user_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], secured_pic_filename))

    # saves the picture's name in the database
    db_collection.update_many({"username":f"{url_username}"}, {"$set": {"pfp":f"{secured_pic_filename}"}}, upsert=False)

    return profile_redirect(url_username)



# --- FORM AUTHENTICATIONS ---
@app.route('/register', methods=['POST'])
def register_authentication():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    # DB QUERY (checks if email is being used)
    db_check_email = db_collection.find_one({"email":f"{email}"})

    if db_check_email:
        flash("That email is already taken. Try a different one", "invalidEmail")
        return render_template('register.html', errorBorderEmail="error-border")
    elif not(db_check_email):

        # DB QUERY (checks if username is taken)
        db_check_username = db_collection.find_one({"username":f"{username}"})

        if db_check_username:
            flash("That username already exists", "invalidUsername")
            return render_template('register.html', errorBorderUsername="error-border")
        elif not(db_check_username):

            hashed_password = generate_password_hash(password)

            join_date = datetime.datetime.now().strftime('%Y-%m-%d')

            db_collection.insert_one({"email":f"{email}", "username":f"{username}", "password":f"{hashed_password}", "name":"No name", "age":"N/A", "gender":"N/A", "date":f"{join_date}", "pfp": ""})
            print("Successfully registered.")
            return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_authentication():

    # if the user's credentials are not stored in the cookies yet then the form data is used for authentication with the database
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    # DB QUERY (checks if email exists)
    db_verify_email = db_collection.find_one({"email":f"{email}"})

    if not(db_verify_email):
        flash("Invalid email address", "incorrectEmail")
        return render_template('login.html', errorBorderEmail="error-border")
    elif db_verify_email:

        # DB QUERY (checks if username exists)
        db_verify_username = db_collection.find_one({"username":f"{username}"})

        if not(db_verify_username):
            flash("Incorrect username", "incorrectUsername")
            return render_template('login.html', errorBorderUsername="error-border")
        elif db_verify_username:

            db_verify_password = check_password_hash(db_verify_username["password"], password)

            if db_verify_password == False:
                flash("Incorrect password", "incorrectPassword")
                return render_template('login.html', errorBorderPassword="error-border")
            elif db_verify_password == True:
                print("Successfully logged in.")
                
                session['verified'] = True # grants access to profile page

                resp = make_response(profile_redirect(db_verify_username["username"])) # passes the user's username as an argument to the profile redirect function 

                # stores user's credentials in cookies for later login
                resp.set_cookie('stored_email', db_verify_username["email"], max_age=86400) # all cookies have 2 mins lifespan (120 seconds)
                resp.set_cookie('stored_username', db_verify_username["username"], max_age=86400)
                resp.set_cookie('stored_password', db_verify_username["password"], max_age=86400)

                return resp


@app.route('/user/logout')
def profile_logout():
    session.pop('verified')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
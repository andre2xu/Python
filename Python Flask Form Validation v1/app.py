import sys
sys.path.append('C:/Users/andre/Documents/Python/Flask-Auth/venv/Lib/site-packages') #adds path of virtual environment modules to the list of system paths

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='./templates')
app.secret_key = 'shhh'

# MySQL database connection configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login_test'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/profile')
def profile(user_data):
    return render_template('profile.html', user = user_data)

# login form
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':        
        username = request.form["username"]
        password = request.form["password"]

        # SQL 1 (checks if user exists in database)
        db_connection_CURSOR1 = mysql.connection.cursor()
        db_connection_CURSOR1.execute('SELECT username FROM accounts WHERE username = %s', (username,))
        results1 = db_connection_CURSOR1.fetchall()

        # if they don't...
        if not(results1):
            flash(u"That username does not exist", "invalidUsername")
            return redirect(url_for('index'))
        
        # if they do...
        elif results1:
            # SQL 2 (retrieves full data of existing user)
            db_connection_CURSOR2 = mysql.connection.cursor() 
            db_connection_CURSOR2.execute('SELECT username, password FROM accounts WHERE username = %s', (username,))
            results2 = db_connection_CURSOR2.fetchall()

            # since the username is already verified, only the password is validated inside this elif statement; it is compared with the hashed password found in the existing user's full data
            db_hashed_password = results2[0][1]
            password_comparison = check_password_hash(db_hashed_password, password)

            if password_comparison == False:
                flash(u"Incorrect password", "invalidPassword")
                return redirect(url_for('index'))
            
            elif password_comparison == True:
                print("Successfully logged in.")
                return profile(results2)

# register form
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':        
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        # SQL (checks if username is taken)
        db_connection_CURSOR3 = mysql.connection.cursor()
        db_connection_CURSOR3.execute('SELECT username FROM accounts WHERE username = %s', (username,))
        results3 = db_connection_CURSOR3.fetchall()
        
        # if it is not taken...
        if not(results3):
            db_connection = mysql.connection
            db_connection.cursor().execute('INSERT INTO accounts (username, password) VALUES (%s, %s)', (username, hashed_password))
            db_connection.commit() #uploads form data to database
            return redirect(url_for('index'))

        # if it is taken...
        elif (results3):
            flash(u"That username is already taken", "takenUsername")
            return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
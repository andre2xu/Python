import sys
sys.path.append('c:/Users/andre/Documents/Python/Flask-Auth/venv/Lib/site-packages')

from flask import Flask, flash, url_for, redirect, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'hidden'
app.config['MONGO_URI'] = 'mongodb+srv://test-admin:1234@practice.lo3nq.mongodb.net/testdb?retryWrites=true&w=majority'
mongodb = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile(user_data):
    return render_template('profile.html', user=user_data)

# register form
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    # SQL (checks if username is already taken)
    results1 = mongodb.db.accounts.find_one({"username": f"{username}"})

    if not(results1):
        mongodb.db.accounts.insert_one({"username":f"{username}", "password":f"{hashed_password}"})
        return redirect(url_for('index'))
    elif results1:
        flash('That username is already taken', 'takenUsername')
        return redirect(url_for('index'))

# login form
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # SQL (checks if user exists)
    results2 = mongodb.db.accounts.find_one({"username": f"{username}"})

    if not(results2):
        flash('Incorrect username', 'invalidUsername')
        return redirect(url_for('index'))
    elif results2:
        password_comparison = check_password_hash(results2["password"], password)

        if password_comparison == False:
            flash('Incorrect password', 'invalidPassword')
            return redirect(url_for('index'))
        elif password_comparison == True:
            return profile(results2)

if __name__ == '__main__':
    app.run()
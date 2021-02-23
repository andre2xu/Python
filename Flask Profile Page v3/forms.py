import sys, os, email_validator

sys.path.append(os.path.dirname(__file__) + '/venv/Lib/site-packages') # connects the path of the root directory (i.e. Flask-Profile) with the module directory and appends the resulting path into the list of pathnames (i.e. sys.path) where Python looks for modules (YOU MAY HAVE TO CHANGE THE STRING PATH)

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import Optional, InputRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired("You cannot leave the email address blank"), Email("Invalid email address format")])
    username = StringField('Username', validators=[InputRequired("You must enter a username")])
    password = PasswordField('Password', validators=[InputRequired("You must enter a password"), Length(max=12, message="Password is too long")])

class RegisterForm(LoginForm):
    pass

class ProfileChanges(FlaskForm):
    change_name = StringField('Change name', validators=[Optional()])
    change_bio = TextAreaField('Bio', validators=[Optional(), Length(max=50, message="Character limit exceeded")])

class AccountChanges(FlaskForm):
    change_email = StringField('Change email address', validators=[Optional(), Email("Invalid email address format")])
    change_username = StringField('Change username', validators=[Optional()])

class PasswordChanges(FlaskForm):
    change_password = PasswordField('Change password', validators=[InputRequired(), Length(max=12, message="Password is too long")])
    confirm_password = PasswordField('Confirm password', validators=[InputRequired(), EqualTo('change_password')])

class BlogPost(FlaskForm):
    blog_title = StringField('Title', validators=[InputRequired(), Length(max=12, message="Title can only be 12 characters long")])
    blog_body = TextAreaField('Blog', validators=[InputRequired(), Length(max=80, message="Please keep the blog short")])
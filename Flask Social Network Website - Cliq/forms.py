import sys, os
ROOT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIRECTORY)

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Optional, Regexp
from wtforms.fields import StringField, PasswordField, TextAreaField

class Login(FlaskForm):
    usernameLog = StringField('Username', validators=[InputRequired(message="You can't leave this empty")])
    passwordLog = PasswordField('Password', validators=[InputRequired(message="You can't leave this empty")])

class Register(FlaskForm):
    usernameReg = StringField('Username', validators=[InputRequired(message="Please enter a valid username"), Length(min=1, max=25, message="That username is too long"), Regexp('^\w+$', message="Username can only contain letters, numbers or underscores. No spaces are allowed")])
    passwordReg = PasswordField('Password', validators=[InputRequired(message="Password field is required"), Length(min=5, max=20, message="Your password should be 5-20 characters long")])

class MyProfileSettings(FlaskForm):
    name = StringField('Change name', validators=[Optional(), Length(min=1, max=25, message="Sorry but your name is too long")])
    bio = TextAreaField('Change bio', validators=[Optional(), Length(max=50, message="Please keep your bio short")])

class MyAccountSettings(FlaskForm):
    change_username = StringField('Change username', validators=[Optional(), Length(min=1, max=25, message="That username is too long"), Regexp('^\w+$', message="Username can only contain letters, numbers or underscores. No spaces are allowed")])
    change_password = PasswordField('Change password', validators=[Optional(), Length(min=5, max=20, message="Your password should be 5-20 characters long")])
    confirm_password = PasswordField('Confirm new password', validators=[EqualTo('change_password', message="Both passwords must match, try again")])

class Clique2Post(FlaskForm):
    caption = TextAreaField('Description', validators=[Length(max=80, message="Caption must be below 80 characters")])
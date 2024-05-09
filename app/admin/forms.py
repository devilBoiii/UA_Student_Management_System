"""
Copyright (c) 2021 - Yangkhor Pvt Ltd
Digital KYC developer team
"""

from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms import validators
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, Email, DataRequired, EqualTo


# login and registration
class LoginForm(FlaskForm):
    username = StringField('Username', id='username_login', validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login', validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username', id='username_create', validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_create', validators=[DataRequired()])
    c_password = PasswordField('Confirm Password', id='pwd_c_create',
                               validators=[DataRequired(), EqualTo('Password', message='Passwords must match')])


class ResetRequestForm(FlaskForm):
     password = PasswordField('Password', id='pwd_create', validators=[DataRequired()])
     c_password = PasswordField('Confirm Password', id='pwd_c_create',
                               validators=[DataRequired(), EqualTo('Password', message='Passwords must match')])

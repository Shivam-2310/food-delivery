"""
AUTHENTICATION FORMS
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """
    LOGIN FORM FOR CUSTOMER AND RESTAURANT OWNER
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    role = RadioField('Login As', choices=[('customer', 'Customer'), ('owner', 'Restaurant Owner')], validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('LOGIN')

class ResetPasswordRequestForm(FlaskForm):
    """
    FORM FOR REQUESTING PASSWORD RESET
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('REQUEST PASSWORD RESET')
    
    def validate_email(self, field):
        """VALIDATE EMAIL EXISTS"""
        user = User.query.filter_by(email=field.data).first()
        if not user:
            raise ValidationError('NO ACCOUNT FOUND WITH THAT EMAIL ADDRESS.')

class ResetPasswordForm(FlaskForm):
    """
    FORM FOR RESETTING PASSWORD
    """
    password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message='PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='PASSWORDS MUST MATCH.')
    ])
    submit = SubmitField('RESET PASSWORD')

class ChangePasswordForm(FlaskForm):
    """
    FORM FOR AUTHENTICATED USERS TO CHANGE PASSWORD
    """
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message='PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='PASSWORDS MUST MATCH.')
    ])
    submit = SubmitField('RESET PASSWORD')
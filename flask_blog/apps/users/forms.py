from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_login import current_user
from flask_babel import _, lazy_gettext as _l

from flask_blog.models import User


class LoginForm(FlaskForm):
    username    = StringField(_l('Username'), validators=[DataRequired()])
    password    = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit      = SubmitField(_l('Sign in'))


class RegistrationForm(FlaskForm):
    username    = StringField(_l('Username'), validators=[DataRequired()])
    email       = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password1   = PasswordField(_l('Password'), validators=[DataRequired()])
    password2   = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password1')])
    submit      = SubmitField(_l('Submit'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_('This username is already taken!'))
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_('This email is already taken!'))


class EditProfileForm(FlaskForm):
    username    = StringField(_l('Username'), validators=[DataRequired()])
    about_me    = TextAreaField(_l('About me'), validators=[Length(min=0, max=150)])
    submit      = SubmitField(_l('Save'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and username.data != current_user.username:
            raise ValidationError(_('This username is already taken!'))


class ChangePasswordForm(FlaskForm):
    old_password    = PasswordField(_l('Old Password'), validators=[DataRequired()])
    new_password    = PasswordField(_l('New Password'), validators=[DataRequired()])
    new_password2   = PasswordField(_l('Repeat New Password'), validators=[DataRequired(), EqualTo('new_password')])
    submit          = SubmitField(_l('Save'))

    def validate_new_password(self, new_password):
        user = User.query.filter_by(username=current_user.username).first()
        if check_password_hash(user.password_hash, new_password.data):
            raise ValidationError(_('Please enter a different password!'))


class RequestPasswordResetForm(FlaskForm):
    email   = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit  = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    new_password    = PasswordField(_l('New Password'), validators=[DataRequired()])
    new_password2   = PasswordField(_l('Repeat New Password'), validators=[DataRequired(), EqualTo('new_password')])
    submit          = SubmitField(_l('Save'))


class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

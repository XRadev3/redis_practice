from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    group = StringField('Group', validators=[DataRequired()])

    submit = SubmitField('Create')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Register')


class UpdateForm(FlaskForm):
    username = StringField('Username')
    name = StringField('Name')
    email = StringField('Email')
    group = StringField('Group')

    submit_info = SubmitField('Update info')

    old_password = PasswordField('Old password')
    new_password = PasswordField('New password')

    submit_pass = SubmitField('Update password')


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

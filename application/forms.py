from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo


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
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Register')


class UpdateForm(FlaskForm):
    username = StringField('Username')
    name = StringField('Name')
    email = StringField('Email')
    group = StringField('Group')

    submit_info = SubmitField('Update info')

    old_password = PasswordField('Old password')
    new_password = PasswordField('New password')
    new_password2 = PasswordField('Repeat new password', validators=[EqualTo('new_password')])

    submit_pass = SubmitField('Update password')


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')


class GroupForm(FlaskForm):
    submit = SubmitField('Submit')

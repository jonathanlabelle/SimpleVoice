from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class SignupForm(FlaskForm):
    companyName = StringField('companyName', validators=[DataRequired()])
    loginName = StringField('loginName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message ='Password must be at least'
                                                                                            ' 5 characters')])
    confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password',
                                                                                    message='Passwords do not match')])
    submit = SubmitField('Create account')


class LogInForm(FlaskForm):
    loginName = StringField('Login Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

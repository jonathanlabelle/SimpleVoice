from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, EmailField, IntegerField
from wtforms.validators import InputRequired, DataRequired, Length, EqualTo, Optional


class SignupForm(FlaskForm):
    companyName = StringField('companyName', validators=[DataRequired()])
    loginName = StringField('loginName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least'
                                                                                            ' 5 characters')])
    confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password',
                                                                                    message='Passwords do not match')])
    submit = SubmitField('Create account')


class LogInForm(FlaskForm):
    loginName = StringField('Login Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class CreateClientForm(FlaskForm):
    clientName = StringField('Client Name', validators=[DataRequired()])
    clientEmail = EmailField('Client e-mail', validators=[DataRequired(), validators.Email()])
    clientPhone = StringField('Client phone number',validators=[DataRequired(), Length(min=10, max=10)])
    clientReference = StringField('Client reference person', validators=[DataRequired()])
    submit = SubmitField('Create account')


class EditClientGetIDForm(FlaskForm):
    clientID = IntegerField('Client ID', validators=[DataRequired()])
    submit = SubmitField('Edit client')


class EditClientInformationForm(FlaskForm):
    clientName = StringField('Client Name', validators=[Optional()])
    clientEmail = EmailField('Client e-mail', validators=[validators.Email(), Optional()])
    clientPhone = StringField('Client phone number', validators=[Length(min=10, max=10), Optional()])
    clientReference = StringField('Client reference person', validators=[Optional()])
    submit = SubmitField('Edit client')


class CreateInvoiceForm(FlaskForm):
    client_id = IntegerField('Client ID', validators=[DataRequired()])
    submit = SubmitField('Create Invoice')


class EditInvoiceGetIDForm(FlaskForm):
    invoice_id = IntegerField('Invoice ID', validators=[Optional()])
    submit = SubmitField('Create Invoice')


class EditInvoiceInformationForm(FlaskForm):
    client_id = IntegerField('New client ID', validators=[Optional()])
    submit = SubmitField('Create Invoice')

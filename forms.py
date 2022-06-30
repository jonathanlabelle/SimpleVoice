from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, EmailField, IntegerField, FloatField, \
    BooleanField
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
    clientPhone = StringField('Client phone number', validators=[DataRequired(), Length(min=10, max=10)])
    clientReference = StringField('Client reference person', validators=[DataRequired()])
    submit = SubmitField('Create client')


class GetIDClientForm(FlaskForm):
    client_id = IntegerField('Client ID', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditClientInformationForm(FlaskForm):
    clientName = StringField('Client Name', validators=[Optional()])
    clientEmail = EmailField('Client e-mail', validators=[validators.Email(), Optional()])
    clientPhone = StringField('Client phone number', validators=[Length(min=10, max=10), Optional()])
    clientReference = StringField('Client reference person', validators=[Optional()])
    submit = SubmitField('Edit client')


class CreateInvoiceForm(FlaskForm):
    client_id = IntegerField('Client ID', validators=[DataRequired()])
    submit = SubmitField('Create Invoice')


class GetIDInvoiceForm(FlaskForm):
    invoice_id = IntegerField('Invoice ID', validators=[Optional()])
    submit = SubmitField('Submit')


class EditInvoiceInformationForm(FlaskForm):
    client_id = IntegerField('New client ID', validators=[Optional()])
    submit = SubmitField('Edit invoice')


class CreateItemForm(FlaskForm):
    item_name = StringField('Item name', validators=[DataRequired()])
    item_price = FloatField('Item price', validators=[DataRequired()])
    submit = SubmitField('Create Item')


class GetIDItemForm(FlaskForm):
    item_id = IntegerField('Item ID', validators=[Optional()])
    submit = SubmitField('Submit')


class EditItemInformationForm(FlaskForm):
    item_name = StringField('Item name', validators=[Optional()])
    item_price = FloatField('Item price', validators=[Optional()])
    submit = SubmitField('Edit item')


class CreateInvoiceLines(FlaskForm):
    invoice_id = IntegerField('Invoice ID', validators=[DataRequired()])
    item_id_1 = IntegerField('Item ID', validators=[DataRequired()])
    quantity_1 = IntegerField('Quantity', validators=[Optional()])
    item_id_2 = IntegerField('Item ID', validators=[Optional()])
    quantity_2 = IntegerField('Quantity', validators=[Optional()])
    item_id_3 = IntegerField('Item ID', validators=[Optional()])
    quantity_3 = IntegerField('Quantity', validators=[Optional()])
    submit = SubmitField('Add invoice lines')


class GetInvoiceLineIDForm(FlaskForm):
    invoice_id = IntegerField('Invoice ID', validators=[DataRequired()])
    item_id = IntegerField('Item ID', validators=[DataRequired()])
    submit = SubmitField('Confirm')


class EditInvoiceLineInformation(FlaskForm):
    item_name = StringField('Item name', validators=[Optional()])
    item_price = FloatField('Item price', validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[Optional()])
    submit = SubmitField('Edit invoice line')


class ConfirmationForm(FlaskForm):
    submit = SubmitField('Confirm')
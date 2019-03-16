from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from opt.models import User, Instrument, Options,MonthC
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


#OPTIONS DATAFORM

class OptionForm(FlaskForm):
    date_calc=StringField('Date Calculation',
                          validators=[DataRequired(), Length(min=2, max=20)])
    ul_name = StringField('Underlying Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    ul_symbol = StringField('Underyling Symbol',
                        validators=[DataRequired(), Length(min=2, max=8)])
    ul_price = StringField('Underyling Price',
                        validators=[DataRequired(), Length(min=2, max=8)])                   
    opt_strike = StringField('Option Strike',
                        validators=[DataRequired(), Length(min=2, max=8)])
    exp_date = StringField('Expiry Date',
                        validators=[DataRequired(), Length(min=2, max=8)])
    date_val=StringField('Date Valorization',
                          validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Calculate')

   
 
class NewInstrument(FlaskForm):
    inst_name = StringField('Instrument Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    inst_des = StringField('Description',
                           validators=[DataRequired(), Length(min=2, max=20)])

 
    submit = SubmitField('Save')

    def validate_instrument(self, inst_name):
        instrument = Instrument.query.filter_by(name_inst=inst_name.data).first()
        if instrument:
            raise ValidationError('That instrument exist already')

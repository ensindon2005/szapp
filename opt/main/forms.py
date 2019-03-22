from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_login import AnonymousUserMixin

'''
class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'
'''

class MessageForm(FlaskForm):
    message = TextAreaField(('Message'), validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')
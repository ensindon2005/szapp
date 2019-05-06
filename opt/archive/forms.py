from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField, SubmitField, PasswordField, BooleanField,SelectField
from wtforms.validators import DataRequired, Length


class DataTypes(FlaskForm):
    datatype = SelectField('Data Type',
        choices=[('empty','----'),('datetime','datetime'),('int64','integer'),
                    ('object','string'),('float','float')])
        
    
    submit = SubmitField('Confirm Format')

    
class Relevant(FlaskForm):
    relevant = SelectField(
        'Data Type',
        choices=[('empty','----'),('opdate','Operation Date'),('ptype','Product'),
                ('underlying','Underlying'),('matmonth','Mat. Month'),('matdate','Mat. Date'),
                    ('myear','Mat.Year'),('uprice','U.Price'),('strike','Strike'),('c_p','Call_Put'),
                    ('q','Quantity'),('ctrsize','Contract Size'),
                    ('optprice','Option Price'),('op','Operation'),('saccount','SubAccount')])
        
    
    submit = SubmitField('Confirm Selection')
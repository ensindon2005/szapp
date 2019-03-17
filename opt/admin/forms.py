from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from opt.models import Instrument,Futures
#from wtforms.ext.sqlalchemy.fields import QuerySelectField


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

#important after validate, the name of the value to validate should be there. Here inst_name()#
    def validate_inst_name(self, inst_name):
        instrument = Instrument.query.filter_by(name_inst=inst_name.data).first()
        if instrument:
            raise ValidationError('That instrument exist already')

class NewFuture(FlaskForm):
    futf_name = StringField('Future Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    futf_sym = StringField('Symbol',
                           validators=[DataRequired(), Length(min=2, max=20)])
  
    #inst = QuerySelectField(query_factory=lambda: Instrument.query.all())
   # inst = QuerySelectField('Instrument', query_factory=lambda: Instrument.query.all())

    submit = SubmitField('Save')

#important after validate, the name of the value to validate should be there. Here inst_name()#
    def validate_futf_name(self, futf_name):
        future = Futures.query.filter_by(fut_name=futf_name.data).first()
        if future:
            raise ValidationError('That future exist already')

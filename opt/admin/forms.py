from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField,TextAreaField,
                    DateField,FloatField,IntegerField)
from wtforms.validators import DataRequired, Length, ValidationError,InputRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from opt.models import Instrument,Futures
from opt.admin.utils import *



#OPTIONS DATAFORM

class OptionForm(FlaskForm):
    date_calc=DateField('Date Calculation', validators=[DataRequired()],
                        format='%Y.%m.%d')
    ul_name = QuerySelectField('Underlying',
                           validators=[DataRequired()], query_factory=get_futures,
                           allow_blank=True, get_label='fut_name')
    ul_price = FloatField('Underyling Price',
                        validators=[DataRequired(), Length(min=2, max=8)])                   
    opt_strike = StringField('Option Strike',
                        validators=[DataRequired(), Length(min=2, max=8)])
    exp_date = DateField('Expiry Date', validators=[DataRequired()],
                        format='%Y.%m.%d')
    date_val=DateField('Date Pricing', validators=[DataRequired()],
                        format='%Y.%m.%d')
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
    inst_id = QuerySelectField('Instrument',
                           validators=[DataRequired()], query_factory=get_instruments,
                           allow_blank=True, get_label='name_inst')
    futf_name = StringField('Future Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    futf_sym = StringField('Symbol',
                           validators=[DataRequired(), Length(min=1, max=20)])
    
    

    submit = SubmitField('Save')

#important after validate, the name of the value to validate should be there. Here futf_name
    def validate_futf_name(self, futf_name):
        future = Futures.query.filter_by(fut_name=futf_name.data).first()
        if future:
            raise ValidationError('That future already exist')
        
       


class CalcForm(FlaskForm):
    entrydate= DateField('Date', validators=[DataRequired()],
                        format='%Y.%m.%d')
    under_n=QuerySelectField('Underlying',
                           validators=[DataRequired()], query_factory=get_futures,
                           allow_blank=True,get_label='fut_name')
    under_p=FloatField('Underlying Price',
                           validators=[InputRequired()])
    date_calc=DateField('Date Pricing', validators=[DataRequired()],
                        format='%Y.%m.%d')
    quantity=IntegerField('Quantity',
                           validators=[DataRequired()])
    vol=FloatField('Volatility (%)',
                           validators=[InputRequired()])


 
    submit = SubmitField('Save')

class AddMonth(FlaskForm):
    month_name = StringField('Month Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    month_letter= StringField('Letter',
                           validators=[DataRequired(), Length(min=1, max=20)])
    
    submit = SubmitField('Save')

    def validate_month_name(self, month_name):
        month = MonthC.query.filter_by(month_name=month_name.data).first()
        if month:
            raise ValidationError(f'This month has been already added')
    

    def validate_month_letter(self, month_letter):
        letter = MonthC.query.filter_by(month_letter=month_letter.data).first()
        if letter:
            raise ValidationError(f'This letter has been already added')



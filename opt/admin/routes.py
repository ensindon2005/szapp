from functools import wraps
from flask_login import login_user, current_user, logout_user, login_required
from opt.admin.forms import NewFuture,NewInstrument,OptionForm,CalcForm, AddMonth
from opt.models import Futures,Options,Instrument,User,MonthC
from flask import render_template, url_for, flash, redirect, request, abort,Blueprint, send_from_directory
import pandas as pd
from os.path import join, dirname, realpath # to get real path
from opt import db



admin=Blueprint('admin',__name__)

UPLOADS_PATH = join(dirname(realpath(__file__)), './static/uploads/')


#implementing a special requirement
def special_requirement(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if 'Edinson' == current_user.username:
                return f(*args, **kwargs) 
            else:
                return redirect(url_for('admin.instrument'))
        except:
            return redirect(url_for('main.index'))
    return wrap


@admin.route('/instrument', methods=['GET', 'POST'])
@special_requirement
def instrument():
    form = NewInstrument()
    if form.validate_on_submit():
        new_inst= Instrument(name_inst=form.inst_name.data, descr_inst=form.inst_des.data)
        db.session.add(new_inst)
        db.session.commit()
        flash(f'The instrument {form.inst_name.data} has been created', 'success')
        return redirect('index')
    return render_template('instruments.html', title='Add Instrument', form=form)


@admin.route('/options_calc', methods=['GET', 'POST'])
def options_calc():
    ## list of all instrument
    form = OptionForm()
    futures=Futures.query.all()
    futctr=Futures.fut_list
    return render_template('options.html', title='Options Calculator', futures=futures,futctr=futctr, form=form)


#admins portal
@admin.route('/admin')
@login_required
def admin_dash():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    instruments = Instrument.query.all()
    users=User.query.order_by(User.id.asc()).all()
   
    return render_template('layoutdash.html', title='Admin Dashboard', 
                    users=users, instruments=instruments, image_file=image_file)




@admin.route('/html_table', methods=("POST", "GET"))
def html_table():
    df=pd.read_excel(UPLOADS_PATH+'futures.xlsx')
    return render_template('view.html', title='excel', tables=[df.to_html(classes='data')], titles=df.columns.values)


@admin.route('/future', methods=['GET', 'POST'])
#@special_requirement
def future():
    form = NewFuture()
    if form.validate_on_submit():
        new_fut= Futures(fut_name=form.futf_name.data, fut_sym=form.futf_sym.data, inst_id=form.inst_id.data.id)
        db.session.add(new_fut)
        db.session.commit()
        flash(f'The future {form.futf_name.data} has been created', 'success')
        
        return redirect('future')
    return render_template('future.html',title='Add future', form=form)

@admin.route('/calculator', methods=['GET','POST'])
def calculator():
    form=CalcForm()
    #check why i can not see this part on the form
    #instrument=Instrument.query.all()
    if form.validate_on_submit():
        #get Form information
        date_calc=request.form.get('entrydate')
        under_name=request.form.get('under_n')
        under_price=request.form.get('under_p')
        date_calc=request.form.get('date_calc')
        quantity=request.form.get('quantity')
        vol=request.form.get('vol')
        return 'GUT gemacht ' + form.under_n.data.fut_sym
    return render_template('calculator.html', title='Calculator', form=form)

@admin.route('/add_month', methods=['GET', 'POST'])
def add_month():
    form=AddMonth()
    if form.validate_on_submit():
        new_month= MonthC(month_name=form.month_name.data, month_letter=form.month_letter.data)
        db.session.add(new_month)
        db.session.commit()
        flash(f'The Month {form.month_name.data} has been added', 'success')
        
        return redirect('add_month')
    return render_template('month.html',title='Add Month', form=form)

'''        
@admin.route("/deletem", methods=['GET','POST'])

def deletem():
    month = MonthC.query.get_or_404(2)

    db.session.delete(month)
    db.session.commit()
    
    return 'the month has been deleted'
'''
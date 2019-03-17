from functools import wraps
from flask_login import login_user, current_user, logout_user, login_required
from opt.admin.forms import NewFuture,NewInstrument,OptionForm
from opt.models import Futures,Options,Instrument
from flask import render_template, url_for, flash, redirect, request, abort,Blueprint, send_from_directory
import pandas as pd
from os.path import join, dirname, realpath # to get real path
from opt import db
from opt.models import User


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
    instruments=Instrument.query.all()
    if form.validate_on_submit():
        inst_id=int(request.form.get(inst_id))
        new_fut= Futures(fut_name=form.futf_name.data, fut_sym=form.futf_sym.data, inst_id=inst_id)
        #missing instrument id
        db.session.add(new_fut)
        db.session.commit()
        flash(f'The future {form.futf_name.data} has been created', 'success')
        return redirect('index')
    return render_template('future.html', title='Add future', form=form, instruments=instruments)
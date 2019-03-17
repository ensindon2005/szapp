from flask import render_template, url_for, flash, redirect, request, abort,Blueprint, send_from_directory
from opt import app, db, bcrypt, mail
from opt.models import *
from functools import wraps
from sqlalchemy import desc, asc
import secrets
import pandas as pd
from pyexcel_xls import get_data # for excel data
from os.path import join, dirname, realpath # to get real path
from datetime import datetime
#from Pillow import Image
from opt.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm, OptionForm,
                             NewFuture, NewInstrument)
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug import secure_filename
import os
from flask_mail import Message



UPLOADS_PATH = join(dirname(realpath(__file__)), './static/uploads/')
UPLOAD_FOLDER='./opt/static/uploads/'
ALLOWED_EXTENSIONS = set(['txt','jpg','pdf','xls','xlsx','ppt','csv'])
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
        return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Your account has been created! You are now able to log in as {form.username.data}', 'success')
        return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
  if current_user.is_authenticated:
        return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
     user = User.query.filter_by(email=form.email.data).first()
     
     if user and bcrypt.check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        flash(f'Welcome Back {current_user.username.capitalize()} !' , 'success')
        return redirect(next_page) if next_page else redirect(url_for('index'))
     else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
  return render_template('login.html', title='Login', form=form)



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (224, 224)
    #i = Image.open(form_picture)
    #i.thumbnail(output_size)
    #i.save(picture_path)

    return picture_fn



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('We miss you already', category='info')
    return redirect(url_for('index'))




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods= ['GET','POST'])
@login_required
def upload():
  if request.method == 'POST':
    # check if the post request has the file part
        if 'inputfile' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['inputfile']

         # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
          #flash('success')
            
            return redirect(url_for('uploaded_file',filename=filename))
        
  return render_template('upload.html')
  
@app.route('/uploaded/<filename>', methods=['GET'])
def uploaded_file(filename):
    flash(f'Your file has been archived', 'success')
    return render_template('uploader.html', filename=filename)
    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
   

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=1000)
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.errorhandler(404)
def errors_404(e):
    return render_template('404.html')

@app.errorhandler(403)
def errors_403(e):
    return render_template('403.html')


@app.errorhandler(500)
def errors_500(e):
    return render_template('500.html')


#implementing a special requirement
def special_requirement(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            if 'Edinson' == current_user.username:
                return f(*args, **kwargs) 
            else:
                return redirect(url_for('instrument'))
        except:
            return redirect(url_for('index'))
    return wrap


@app.route('/instrument', methods=['GET', 'POST'])
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


@app.route('/options_calc', methods=['GET', 'POST'])
def options_calc():
    ## list of all instrument
    form = OptionForm()
    futures=Futures.query.all()
    futctr=Futures.fut_list
    return render_template('options.html', title='Options Calculator', futures=futures,futctr=futctr, form=form)


#admins portal
@app.route('/admin')
@login_required
def admin_dash():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    instruments = Instrument.query.all()
    users=User.query.all()
   
    return render_template('layoutdash.html', title='Admin Dashboard', 
                    users=users, instruments=instruments, image_file=image_file)

'''
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
'''



@app.route('/html_table', methods=("POST", "GET"))
def html_table():
    df=pd.read_excel(UPLOADS_PATH+'futures.xlsx')
    return render_template('view.html', title='excel', tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/future', methods=['GET', 'POST'])
#@special_requirement
def future():
    form = NewFuture()
    if form.validate_on_submit():
        
        new_fut= Futures(fut_name=form.futf_name.data, fut_sym=form.futf_sym.data, inst_id=form.inst.data)
        #missing instrument id
        db.session.add(new_fut)
        db.session.commit()
        flash(f'The future {form.futf_name.data} has been created', 'success')
        return redirect('index')
    return render_template('future.html', title='Add future', form=form)
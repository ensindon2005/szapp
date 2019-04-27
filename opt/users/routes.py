from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort,Blueprint, send_from_directory,g
from flask_login import login_user, current_user, logout_user, login_required
from opt import db, bcrypt
from opt.users.forms import (RegistrationForm,LoginForm,UpdateAccountForm,
                            RequestResetForm,ResetPasswordForm)
from opt.users.utils import save_picture,send_reset_email
from opt.models import User,Post,FileContent,Business
import os
from werkzeug import secure_filename


users=Blueprint('users',__name__)

UPLOADS_FOLDER =  './opt/static/uploads/'

@users.before_request
def before_request():
    if current_user.is_authenticated:
        #g.user = current_user.get_id()
        current_user.last_seen = datetime.utcnow()
       # g.user = current_user.get_id() # return username in get_id()
        db.session.commit()
    #else:
      #  g.user = None
        



@users.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
        return redirect(url_for('main.index'))
  form = RegistrationForm()
  if form.validate_on_submit():
      #Creating upload folder for user
        name_folder=form.company.data
        path=os.path.join(UPLOADS_FOLDER,name_folder)
        if not os.path.isdir(path):
            os.mkdir(path)
            business=Business(bizname=form.company.data,folder_path=path)
            db.session.add(business)
            db.session.commit()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data.lower(), company=business,
                    email=form.email.data.lower(), password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        

        flash(f'Your account has been created! You are now able to log in as {form.username.data}', 'success')
        return redirect(url_for('users.login'))
  return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['GET','POST'])
def login():
  if current_user.is_authenticated:
        return redirect(url_for('main.index'))
  form = LoginForm()
  if form.validate_on_submit():
     user = User.query.filter_by(email=form.email.data).first()
     
     if user and bcrypt.check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        flash(f'Welcome Back {current_user.username.capitalize()} !' , 'success')
        return redirect(next_page) if next_page else redirect(url_for('main.index'))
     else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
  return render_template('login.html', title='Login', form=form)

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    business=current_user.company
    if current_user.company==None:
        path=os.path.join(UPLOADS_FOLDER,current_user.username.lower())
    else:
         path=current_user.company.folder_path
       # path= os.path.join(UPLOADS_FOLDER,current_user.company.lower())
    if not os.path.isdir(path):
            os.mkdir(path)
    

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data

       # current_user.company = form.company.data
        
        db.session.commit()
       
       # npath=os.path.join(UPLOADS_FOLDER,form.company.data.lower())
       # if os.path.isdir(path) != os.path.isdir(npath):
        #    os.rename(path,npath)
         #   files = current_user.files_saved
          #  for i in range(len(files)):
           #     file=current_user.files_saved[i]
            #    filename = file.filename
             #   file.path_file=os.path.join(npath,filename)
              #  db.session.commit()

        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        company=current_user.company.bizname
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form,company=company)


@users.route("/logout")
def logout():
    logout_user()
    flash('We miss you already', category='info')
    return redirect(url_for('main.index'))


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=1000)
    return render_template('user_posts.html', posts=posts, user=user)



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)



@users.route('/follow/<username>')
@login_required
def follow(username):
    if current_user.is_authenticated:
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('users.users_posts', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username),'info')
        return redirect(url_for('users.user_posts', username=username))
    return 'Please log in'



@users.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('users.user_posts', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username),'danger')
    return redirect(url_for('users.user_posts', username=username))
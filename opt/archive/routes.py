import os
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, url_for, flash, redirect, request, 
                    abort,Blueprint, send_from_directory,current_app)
from opt.users.utils import *
from werkzeug import secure_filename


archives=Blueprint('archives',__name__)



@archives.route('/upload', methods= ['GET','POST'])
#@login_required
def upload():
  if request.method == 'POST':
    # check if the post request has the file part
        if 'inputfile' not in request.files:
            flash('Please add a file!','danger')
            return redirect(request.url)
        file = request.files['inputfile']

         # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
            
            
            return redirect(url_for('archives.uploaded_file',filename=filename))
        
  return render_template('upload.html')
  
@archives.route('/uploaded/<filename>', methods=['GET'])
def uploaded_file(filename):
    flash(f'Your file has been archived', 'success')
    return render_template('uploader.html', filename=filename)
    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


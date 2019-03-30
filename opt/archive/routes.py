import os
from io import BytesIO,StringIO
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, url_for, flash, redirect, request, 
                    abort,Blueprint, send_from_directory,current_app,send_file)
from opt.users.utils import *
from werkzeug import secure_filename
from opt.archive.utils import allowed_file
from opt.models import *
from opt import db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


archives=Blueprint('archives',__name__)

#UPLOADS_PATH = join(dirname(realpath(__file__)), './static/uploads/')
#UPLOADS_FOLDER =  current_app.config['UPLOAD_FOLDER']

@archives.route('/list', methods=['GET','POST'])
@login_required
def listfiles():
  folder=current_user.username
  files=os.listdir(current_app.config['UPLOAD_FOLDER']+folder)

  
  return render_template('list.html',folder=folder, files=files)

@archives.route('/pandas/<filename>', methods=['GET','POST'])
@login_required
def pandas(filename):
    path=os.path.join(current_app.config['UPLOAD_FOLDER'],current_user.username)
    df=pd.read_excel(path+'/'+filename)
    
    #df.plot(kind='bar',x='modelo',y='price')
    headers=df.columns.values      
    rows=df.itertuples(index=False)  

   
    #df=pd.read_excel('futures.xlsx')
    #return render_template('pandas1.html',data=df.itertuples())
    return render_template('pandas1.html',data=rows,headers=headers)
    #a=plt.show()
    #return render_template('pandas.html', bild=a,title='excel', 
                     #   tables=[df.to_html(classes='data', index=False)], titles=df.columns.values)




@archives.route('/upload', methods= ['GET','POST'])
@login_required
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
            folder=current_user.username
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],folder,filename))
            
            return redirect(url_for('archives.uploaded_file',filename=filename))
        
  return render_template('upload.html')

@archives.route('/uploaded/<filename>', methods=['GET'])
def uploaded_file(filename):
      flash(f'Your file has been archived', 'success')
      return render_template('uploader.html')
    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


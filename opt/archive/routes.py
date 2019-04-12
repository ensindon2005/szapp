import os
import csv
from io import BytesIO,StringIO
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, url_for, flash, redirect, request, 
                    abort,Blueprint, send_from_directory,current_app,send_file)
from opt.users.utils import *
from werkzeug import secure_filename
from opt.archive.utils import allowed_file
from opt.errors.routes import *
from opt.models import *
from opt import db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from os.path import join, dirname, realpath

archives=Blueprint('archives',__name__)

excel=['xls','xlsx']
csv=['csv','txt']
encodes = ["utf8", "cp1252"]
basedir = os.path.abspath(os.path.dirname(__file__))

@archives.route('/list', methods=['GET','POST'])
@login_required
def list_files():
  folder=current_user.username
  files=os.listdir(current_app.config['UPLOAD_FOLDER']+current_user.username)
  
  return render_template('list.html',folder=folder, files=files)

@archives.route('/download/<filename>')
@login_required
def download(filename):
        # no best solution but it is working
        fbase= os.path.join('./static/uploads/',current_user.username,filename)
        #ruta=os.path.abspath(filename)
        #file=os.path.join(path,filename)
        #file=os.path.join(current_app.config['UPLOAD_FOLDER'],current_user.username,filename)
        #return send_file(filename=filename, as_attachment=True)
        return send_file(fbase,filename,as_attachment=True)
  

  


@archives.route('/pandas/<filename>', methods=['GET','POST'])
@login_required
def pandas(filename):
    path_file=os.path.join(current_app.config['UPLOAD_FOLDER'],current_user.username,filename)
    extension=filename.split('.')[-1]
    if extension in excel:
        #df=pd.read_excel(path) 
       df=pd.read_excel(path_file,index_col=False)

    elif extension in csv:
       try:
            df=pd.read_csv(path_file, sep=';', encoding=encodes[0],index_col=False)
            
       except:
            df=pd.read_csv(path_file,sep=';',encoding=encodes[1],index_col=False)
            
    else:
          flash(f'I can not work this format', 'danger')
    
    headers=df.columns.values
    before=list(df.dtypes)
    after=[]
    for header in headers:
         if df[header].dtype == object:
            df[header] = df[header].astype(str)
            a='string'            
         else:
            a = 'number'
         after.append(a)
    rows=df.itertuples(index=False)

    #return render_template('pandas1.html',data=df.itertuples())
    return render_template('pandas1.html',data=rows,headers=headers,dtypes=after,df=df)

@archives.route('/format/<filename>', methods=['GET','POST'])
def format_file(filename):
      formats={'String':'string', 'number':'number',}
      return 'to format columns'
   

@archives.route('/upload', methods= ['GET','POST'])
@login_required
def upload():
  if request.method == 'POST':
        folder=current_user.username
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
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],folder,filename))
            
            return redirect(url_for('archives.uploaded_file',filename=filename))
        
  return render_template('upload.html')



@archives.route('/uploaded/<filename>', methods=['GET'])
def uploaded_file(filename):
      flash(f'Your file has been archived', 'success')
      return render_template('uploader.html')
    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


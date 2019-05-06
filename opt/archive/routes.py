import os
import csv
from io import BytesIO,StringIO
from flask_login import login_user, current_user, logout_user, login_required
from flask import (render_template, url_for, flash, redirect, request, 
                    abort,Blueprint, send_from_directory,current_app,send_file, session)
from opt.users.utils import *
from werkzeug import secure_filename
from opt.archive.utils import *
from opt.errors.routes import *
from opt.models import *
from opt import db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from os.path import join, dirname, realpath
from opt.archive.forms import DataTypes, Relevant



archives=Blueprint('archives',__name__)

excel=['xls','xlsx']
csv=['csv','txt']
encodes = ["utf8", "cp1252"]
xfile=[]
csfile=[]

@staticmethod
def filesaved(current_user,xfile,csfile):
       fsaved=FileContent.query.filter_by(user_id=current_user.id).all()
       
       for file in fsaved:
              if file.extension in excel:
                 xfile.append(file.id)
              else:
                     csfile.append(file.id)

       return fsaved

#fsaved=FileContent.query.filter_by(user_id=current_user.id).all()

@archives.route('/upload', methods= ['GET','POST'])
@login_required
def upload():
  if request.method == 'POST':
        folder=current_user.company.folder_path
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
            
            path_file=os.path.join(folder,filename)
            file.save(path_file)
            new_file=FileContent(filename=filename,path_file=path_file,extension=extension(filename),
                                 data=file.read(), user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            flash(f'The File {filename} has been uploaded', 'success')
            return redirect(url_for('archives.upload',filename=filename))
        
  return render_template('upload.html')



@archives.route('/list', methods=['GET','POST'])
@login_required
def list_files():
  folder=current_user.company.folder_path
  fsaved=FileContent.query.filter_by(user_id=current_user.id).all()
  lsfiles=[]
  uploads=[]
  for file in fsaved:
         lsfiles.append(file.filename)
         date=file.date_upload.strftime('%d-%m-%Y  %H:%M:%S')
         uploads.append(date)
   
   #Using the list of files in folder (use code below)
  #listfiles=[]
  #files=os.listdir(current_app.config['UPLOAD_FOLDER']+folder)
  #files=os.listdir(folder)
  #for file in files:
  #       if allowed_file(file):
    #            listfiles.append(file)        
  
  return render_template('list.html',folder=current_user.company.bizname,files=lsfiles,
                           uploads=uploads)


@archives.route('/explore/<filename>')
@login_required
def explore(filename):
    form = DataTypes()
    fsaved=FileContent.query.filter_by(filename=filename).first()
    #path_file=fsaved.path_file
    #path_file=os.path.join(current_user.company.folder_path,filename)
   
    if fsaved.extension in excel:
       df=pd.read_excel(fsaved.path_file,index_col=False)
    elif fsaved.extension in csv:
       try:
            df=pd.read_csv(fsaved.path_file, sep="\s*,\s*", encoding=encodes[0],index_col=False,engine='python')
            
       except:
            df=pd.read_csv(fsaved.path_file,sep="\s*,\s*",encoding=encodes[1],index_col=False,engine='python')    
    
    df=df.iloc[0:1]
    headers=df.columns.values

    before=list(df.dtypes)
   # after=[]
    #for header in headers:
     #    if df[header].dtype == object:
      #      df[header] = df[header].astype(str)
       #     a='string'  
        # elif df[header].dtype == float:   
         #   a='float' 
         #elif df[header].dtype == int:
          #  a='integer'    
         #else:
          #  a = 'datetime'
         #after.append(a)
   # safter=list(set(after))
    
    
    return render_template('explore.html', form=form,headers=headers,filename=filename,df=df,
                           before=before,fsaved=fsaved)


@archives.route('/datatype/<filename>', methods=['GET','POST'])
def datatype(filename):
      form=DataTypes()
      dat=session.get('data')
      #ndata = pd.DataFrame.from_dict(dat)
      data=request.form.getlist('datatype')
      file = FileContent.query.filter_by(filename=filename).first()

      if file.extension in excel:
          df=pd.read_excel(file.path_file,index_col=False)
      elif file.extension in csv:
          try:
            df=pd.read_csv(file.path_file, sep="\s*,\s*", encoding=encodes[0],index_col=False,engine='python')
            
          except:
             df=pd.read_csv(file.path_file,sep="\s*,\s*",encoding=encodes[1],index_col=False,engine='python')    
      headers=df.columns.values
      
      return  ( str(headers))


@archives.route('/relevant/<filename>', methods=['GET','POST'])
def relevant(filename):
      form=Relevant()
      file = FileContent.query.filter_by(filename=filename).first()

      if file.extension in excel:
          df=pd.read_excel(file.path_file,index_col=False)
      elif file.extension in csv:
          try:
            df=pd.read_csv(file.path_file, sep="\s*,\s*", encoding=encodes[0],index_col=False,engine='python')
            
          except:
             df=pd.read_csv(file.path_file,sep="\s*,\s*",encoding=encodes[1],index_col=False,engine='python')    
      headers=df.columns.values
      return  render_template('relevant.html', form=form, df=df, headers=headers,filename=filename)

@archives.route('/finalized/<filename>', methods=['GET','POST'])
def finalized(filename):
    file = FileContent.query.filter_by(filename=filename).first()
    if file.extension in excel:
          df=pd.read_excel(file.path_file,index_col=False)
    elif file.extension in csv:
          try:
            df=pd.read_csv(file.path_file, sep="\s*,\s*", encoding=encodes[0],index_col=False,engine='python')
            
          except:
             df=pd.read_csv(file.path_file,sep="\s*,\s*",encoding=encodes[1],index_col=False,engine='python')    
    headers=df.columns.values

    #new dataframe for working data
    df2=pd.DataFrame()
    #selection of relevant columns
    relcols=request.form.getlist('relevant')
    for item in relcols:
         if item !='empty':
            df2[headers[relcols.index(item)]]=df[headers[relcols.index(item)]]
    
    return (str(df2))

@archives.route('/download/<filename>')
@login_required
def download(filename):
        UPLOAD_FOLDER='./static/uploads/'
        # no best solution but it is working
        fbase= os.path.join(UPLOAD_FOLDER,current_user.company.bizname,filename)
        #fbase=current_user.company.bizname
        ruta=os.path.abspath(filename)
        #file=os.path.join(path,filename)
        #file=os.path.join(current_app.config['UPLOAD_FOLDER'],current_user.username,filename)
        #return send_file(filename=filename, as_attachment=True)
        return send_file(fbase,filename,as_attachment=True)


@archives.route('/reading/<filename>')
@login_required
def reading(filename):
        file_data=FileContent.query.get(16)
        content=BytesIO(file_data.data)
        
        return send_file(BytesIO(file_data.data), attachment_filename='file.xls',as_attachment=True)



@archives.route('/delete/<filename>', methods=['GET','POST'])
@login_required
def delete(filename):
    file= FileContent.query.filter_by(filename=filename).first()
    os.remove(file.path_file)
    db.session.delete(file)
    db.session.commit()
    
    flash(f'The file {file.filename} has been deleted', 'danger')
    return redirect(url_for('archives.list_files'))
    







@archives.route('/pandas/<filename>', methods=['GET','POST'])
@login_required
def pandas(filename):
    path_file=os.path.join(current_user.company.folder_path,filename)
    extension=filename.split('.')[-1]
    if extension in excel:
       df=pd.read_excel(path_file,index_col=False)

    elif extension in csv:
       try:
            df=pd.read_csv(path_file, sep="\s*,\s*", encoding=encodes[0],index_col=False)
            
       except:
            df=pd.read_csv(path_file,sep="\s*,\s*",encoding=encodes[1],index_col=False)
            
    else:
          flash(f'I can not work this format', 'danger')
    
    headers=df.columns.values
    df=df.iloc[0:5]
    rows=df.itertuples(index=False)

    #return render_template('pandas1.html',data=df.itertuples())
    return render_template('pandas1.html',data=rows,headers=headers,
                           dtables=[df.to_html(classes='data')],
                              titles=df.columns.values,filename=filename)


   




@archives.route('/uploaded/<filename>', methods=['GET'])
def uploaded_file(filename):
      flash(f'Your file has been archived', 'success')
      return render_template('uploader.html')


     







ALLOWED_EXTENSIONS = set(['txt','jpg','pdf','xls','xlsx','ppt','csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def extension(filename):
    return filename.split('.')[1]
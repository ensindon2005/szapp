import os


UPLOAD_FOLDER='./opt/static/uploads/'

class Config:
    POSTGRES = {
    'user': 'test_user',
    'pw': 'maflita2007',
    'db': 'szapp',
    'host': 'localhost',
    'port': '5432',
}


    POSTS_PER_PAGE= 25
    UPLOAD_FOLDER=  UPLOAD_FOLDER
    SECRET_KEY=os.urandom(24).hex()
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
                                             %(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    SQLALCHEMY_TRACK_MODIFICATIONS = False
  
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD= os.environ.get('EMAIL_PASS')

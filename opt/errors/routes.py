from flask import render_template,redirect,Blueprint
from opt import db

errors=Blueprint('errors',__name__,template_folder='templates')



@errors.errorhandler(404)
def errors_404(e):
    return render_template('404.html')

@errors.errorhandler(403)
def errors_403(e):
    return render_template('403.html')


@errors.errorhandler(500)
def errors_500(e):
    db.session.rollback()
    return render_template('500.html')
from flask import render_template,redirect,Blueprint

errors=Blueprint('errors',__name__)



@errors.errorhandler(404)
def errors_404(e):
    return render_template('404.html')

@errors.errorhandler(403)
def errors_403(e):
    return render_template('403.html')


@errors.errorhandler(500)
def errors_500(e):
    return render_template('500.html')
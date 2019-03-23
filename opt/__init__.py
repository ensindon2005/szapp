from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
from flask_mail import Mail
from config import Config
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_bootstrap import Bootstrap


bootstrap = Bootstrap()
db = SQLAlchemy()
bcrypt=Bcrypt()
login_manager=LoginManager()
migrate = Migrate()
#manager = Manager()

login_manager.login_view = 'users.login'
#login_manager.anonymous_user = Anonymous
login_manager.login_message_category = 'info'
mail=Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    bootstrap.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    



    from opt.users.routes import users
    from opt.post.routes import posts
    from opt.main.routes import main
    from opt.archive.routes import archives
    from opt.admin.routes import admin
    from opt.errors.routes import errors

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(archives)
    app.register_blueprint(admin)
    app.register_blueprint(errors)

    return app
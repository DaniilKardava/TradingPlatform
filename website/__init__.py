from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "super secret key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # from file import variables
    from .views import views

    with app.app_context():
        db.create_all()

    # Sets the prefix required to access route defined in auth and views files
    # ex. "/view/" -> url would require this prefix prior to the route specified in files
    app.register_blueprint(views, url_prefix="/")

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create sql database. Function below will check if database with this name exists, if not, it will create it.
db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "super secret key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # from views file import variable views
    from .views import views

    # Syntax to create database
    with app.app_context():
        db.create_all()

    # Sets the prefix required to access route defined in auth and views files
    # ex. "/view/" -> url would require this prefix prior to the route specified in files
    app.register_blueprint(views, url_prefix="/")

    return app

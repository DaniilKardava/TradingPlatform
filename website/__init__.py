from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create sql alchemy object. (Database)
db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    
    # Create flask app
    app = Flask(__name__)
    
    # Key to secure app session
    app.config["SECRET_KEY"] = "super secret key"
    
    # Set the database uri. Stored locally. 
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    
    # Sets up database for use with this flask application 
    db.init_app(app)

    # from views file import variable views
    from .views import views

    # Syntax to create database for the application. Automatically checks for existing database, creates one if it doesnt exist yet.
    with app.app_context():
        db.create_all()

    # Register the endpoints defined in the views file. Does not set any additional prefix to reach endpoints that are part of the "views blueprint".
    app.register_blueprint(views, url_prefix="/")

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from country_list import countries_for_language


class Base(DeclarativeBase):
  pass

app = Flask(__name__)
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///collabhub.db"
app.config["SECRET_KEY"] = "Veryverytopsecret909090"
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

countries = countries_for_language("en")
list_of_countries = [country[1] for country in countries]

from collabhub.routes import *
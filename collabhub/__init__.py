from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
  pass

app = Flask(__name__)
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///collabhub.db"
db.init_app(app)
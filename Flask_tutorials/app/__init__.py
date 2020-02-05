from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")

elif app.config["ENV"] == "testing":
    app.config.from_object("config.TestingConfig")

else :
    app.config.from_object("config.DevelopmentConfig")
import redis
from rq import Queue

r = redis.Redis()
q = Queue(connection=r)
from app import views
from app import admin_views
from app import errorhandler


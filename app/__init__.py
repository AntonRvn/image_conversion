from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://postgres:2252262446@localhost:5432/cartoonify_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def login_user(id):
    return User.query.get(int(id))

from app import routes, models
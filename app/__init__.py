from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2252262446@localhost:5432/cartoonify_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def login_user(id):
    return User.query.get(int(id))

from app import routes, models

#if __name__ == '__main__':
#    app.run(debug=True)  # Только для локального запуска
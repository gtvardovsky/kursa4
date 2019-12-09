from flask import Flask

from config import Config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'xxxxyyyyyzzzzz'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Пожалуйста, войдите, чтобы открыть эту страницу."
bootstrap = Bootstrap(app)
app.static_folder = 'static'


from app import routes, models



import os
import psycopg2
from flask_login import LoginManager, UserMixin


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'


conn = psycopg2.connect(dbname='kursa4', user='postgres', password='13001', host='127.0.0.1')

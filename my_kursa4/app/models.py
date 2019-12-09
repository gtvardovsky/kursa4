from _md5 import md5
import re
from app import login_manager
from flask_login import UserMixin
from config import conn

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.set_username()
        self.set_name_()
        self.set_surname_()
        self.set_experience_()
        self.set_datebirth_()
        self.set_carnumber_()
        self.set_isadmin()
        self.set_car_model()

    def set_username(self):
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM driver WHERE id = '{}'".format(self.id))
        _username = cursor.fetchone()
        self.username = _username[0]

    def set_username_(self, username):
        self.username = username

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        default = 'https://bootdey.com/img/Content/avatar/avatar1.png'
        return 'https://www.gravatar.com/avatar/{}?d=default&s={}'.format(digest, size)

    def set_surname_(self):
        cursor = conn.cursor()
        cursor.execute("SELECT surname FROM driver WHERE id = '{}'".format(self.id))
        _surname = cursor.fetchone()
        self.surname = _surname[0]

    def set_surname(self, surname):
        self.surname = surname

    def set_name(self, name):
        self.name = name

    def set_name_(self):
        cursor = conn.cursor()
        cursor.execute("SELECT namedriver FROM driver WHERE id = '{}'".format(self.id))
        _namedriver= cursor.fetchone()
        self.namedriver = _namedriver[0]

    def set_experience(self,experience):
        self.experience = experience

    def set_experience_(self):
        cursor = conn.cursor()
        cursor.execute("SELECT experience FROM driver WHERE id = '{}'".format(self.id))
        _experience = cursor.fetchone()
        self.experience = _experience[0]

    def set_carnumber(self,carnumber):
        self.carnumber = self.get_carNumber_from_id(carnumber)
        print('car_number = {}'.format(self.carnumber))

    def set_carnumber_(self):
        cursor = conn.cursor()
        cursor.execute("SELECT carnumber FROM driver WHERE id = '{}'".format(self.id))
        carnumber = cursor.fetchone()
        self.id_car = carnumber[0]
        if carnumber[0] is not None:
            self.carnumber = self.get_carNumber_from_id(self.id_car)

    def set_datebirth(self, datebirth):
        self.datebirth = self.dateBirth_toNormal_View(datebirth)

    def set_datebirth_(self):
        cursor = conn.cursor()
        cursor.execute("SELECT datebirth FROM driver WHERE id = '{}'".format(self.id))
        _datebirth = cursor.fetchone()
        if _datebirth[0] is not None:
            self.datebirth = self.dateBirth_toNormal_View(_datebirth[0])

    def set_isadmin(self):
        cursor = conn.cursor()
        cursor.execute("SELECT isadmin FROM driver WHERE id = '{}'".format(self.id))
        _isadmin = cursor.fetchone()
        self.isadmin = _isadmin[0]

    def dateBirth_toNormal_View(self, dateBirth):
        pars = re.split(r'\-', str(dateBirth))
        formated_dateBirth = pars[2] + '.' + pars[1] + '.' + pars[0]
        return formated_dateBirth

    def get_carNumber_from_id(self, car_id):
        cursor = conn.cursor()
        cursor.execute("SELECT carnumber FROM car WHERE id_car = '{}'".format(car_id))
        car_number = cursor.fetchone()
        return car_number[0]

    def set_car_model(self):
        if self.id_car is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT carname FROM car WHERE id_car = '{}'".format(self.id_car))
            car_model = cursor.fetchone()
            self.car_model = car_model[0]









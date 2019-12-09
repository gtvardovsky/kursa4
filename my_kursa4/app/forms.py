from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import re
from config import conn


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM driver ")
        loginList = cursor.fetchall()
        for login in loginList:
            if username.data == login[0]:
                raise ValidationError('Этот username уже занят, попробуйте другой')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[Length(min=0, max=25)])
    name = StringField('Имя', validators=[Length(min=0, max=25)])
    # carnumber = StringField('Номер машины', validators=[DataRequired()])
    datebirth = StringField('Дата рождения', validators=[DataRequired()])
    submit = SubmitField('Submit')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    def validate_datebirth(self, datebirth):
        match = re.search(r'\d\d\.\d\d\.\d{4}', datebirth.data)
        if not match:
            raise ValidationError('Соблюдай формат (ДД.ММ.ГГГГ)')

    def validate_username(self, username):
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM driver ")
        loginList = cursor.fetchall()
        print('cur_us.username = {}'.format(current_user.username))
        if not current_user.username == username.data:
            for login in loginList:
                if username.data == login[0]:
                    raise ValidationError('Этот username уже занят, попробуйте другой')

    def validate_carnumber(self, carnumber):
        print(current_user.isadmin)
        if not current_user.carnumber and not current_user.isadmin:
            cursor = conn.cursor()
            cursor.execute("SELECT carnumber FROM car")
            carnumberList = cursor.fetchall()
            flagNumber = True
            flagID = False
            for number in carnumberList:
                if carnumber.data == number[0]:
                    flagNumber = False
            cursor.execute("SELECT id_car from car WHERE carnumber = '{}'".format(carnumber.data))
            bla = cursor.fetchone()
            idCar = bla[0]
            cursor.execute("SELECT carnumber FROM driver")
            id_curnumberList = cursor.fetchall()
            for id in id_curnumberList:
                if idCar == id[0]:
                    flagID = True
            str = None
            if flagNumber:
                str = 'Такого номера машины нет в базе. Обратитесь к администратору'
            if flagID:
                str = 'Эта машина принадлежит другому водителю, введите другой номер'
            if str:
                raise ValidationError('{}'.format(str))


def parserDateStr(str):
    pars = re.split(r'\.', str)
    # year = pars[2]
    # month = pars[1]
    # day = pars[0]
    newStr = pars[2] + '-' + pars[1] + '-' + pars[0]
    return newStr


class AddOrderForm(FlaskForm):
    client = StringField('client')
    product = StringField('product', validators=[DataRequired()])
    driver = StringField('driver')
    date_delivery = StringField('date_delivery', validators=[DataRequired()])
    weight = StringField('weight', validators=[DataRequired()])
    city_A = StringField('city_A', validators=[DataRequired()])
    city_B = StringField('city_B', validators=[DataRequired()])
    status = StringField('status')
    submit = SubmitField('add_order')

    # def validate_client(self, client):
    #     print('CLIENT = {}'.format(client.data))
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT nameofclient FROM client")
    #     flagClient = True
    #     client_list = cursor.fetchall()
    #     for _client in client_list:
    #         if client.data == _client[0]:
    #             flagClient = False
    #     if flagClient:
    #         raise ValidationError('Такого клиента нет в базе')
    #
    # def validate_driver(self, driver):
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT username FROM driver")
    #     flagDriver = True
    #     driver_list = cursor.fetchall()
    #     for _driver in driver_list:
    #         if driver.data == _driver[0]:
    #             flagDriver = False
    #     if flagDriver:
    #         raise ValidationError('Такого водителя нет в базе')
    #
    # def validate_status(self, status):
    #     if not (status == 'Доставлен' or status == 'Не доставлен'):
    #         raise ValidationError("'Доставлен' или 'Не доставлен'")



class AddClientForm(FlaskForm):
    client_name = StringField('client_name', validators=[DataRequired()])
    client_telephone = StringField('client_telephone', validators=[DataRequired()])
    client_card = StringField('client_card', validators=[DataRequired()])
    submit = SubmitField('add_client')


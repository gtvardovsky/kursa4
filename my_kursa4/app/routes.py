import re

from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from datetime import datetime

from app import app
from flask import render_template, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddOrderForm, parserDateStr, AddClientForm
from app.models import User
from config import conn
from app.forms import parserDateStr

global form, user


@app.route('/')
def mainPage():
    return redirect(url_for('login'))


@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home', user=user)


@app.route('/admin_panel/<username>', methods=['GET', 'POST'])
@login_required
def admin_panel(username):
    cursor = conn.cursor()
    cursor.execute("SELECT username from driver")
    usernameList = cursor.fetchall()
    cursor.execute("SELECT * from driver")
    driverList = cursor.fetchall()
    listDrivers = createListDriver(driverList)
    cursor.execute("SELECT * from orders")
    orderList = cursor.fetchall()
    listOrders = createListOrder(orderList)
    cursor.execute("SELECT nameofclient from client")
    cclientList = cursor.fetchall()
    clientList = []
    succedOrder = calculate_succedOrder()
    inWorkOrder = calculate_inWorkOrder()
    for client in cclientList:
        clientList.append(client[0])
    for _username in usernameList:
        if _username[0] == username:
            cursor.execute("SELECT id FROM driver WHERE username = '{}'".format(username))
            id = cursor.fetchone()
            user = User(id[0])
            edit_form = EditProfileForm()
            addOrder_form = AddOrderForm()
            addClient_form = AddClientForm()
            print(listOrders)
            if addOrder_form.validate_on_submit():
                print("YES")
                update_orderData(addOrder_form)
            if edit_form.validate_on_submit():
                update_userData(username, edit_form)
            if addClient_form.validate_on_submit():
                update_clientData(addClient_form)
            if not user.isadmin:
                return redirect(url_for('index'))
            return render_template('admin_panel.html', user=user, drivers=listDrivers, orders = listOrders, form = edit_form, form2 = addOrder_form, form3 = addClient_form, clients = clientList, succedOrder = succedOrder, inWorkOrder = inWorkOrder)
    return render_template('404.html'), 404

def calculate_succedOrder():
    cursor = conn.cursor()
    cursor.execute("SELECT count(id_order) FROM orders WHERE is_delivery = true")
    answer = cursor.fetchone()
    return answer[0]

def calculate_inWorkOrder():
    cursor = conn.cursor()
    cursor.execute("SELECT count(id_order) FROM orders WHERE is_delivery = false")
    answer = cursor.fetchone()
    return answer[0]

def createChoicesFor_driver():
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM driver")
    drivers = cursor.fetchall()
    driversList = []
    for driver in drivers:
        driversList.append(driver[0])
    print('driverList = {}'.format(driversList))
    return driversList

def createChoicesFor_client():
    cursor = conn.cursor()
    cursor.execute("SELECT nameofclient FROM client")
    clients = cursor.fetchall()
    clientsList = []
    for client in clients:
        clientsList.append(client[0])
    return clientsList

def update_orderData(addOrderForm):
    cursor = conn.cursor()
    list_id = fromStrToID(addOrderForm.driver.data,addOrderForm.client.data, addOrderForm.product.data, addOrderForm.weight.data, addOrderForm.date_delivery.data,addOrderForm.status.data, addOrderForm.city_A.data, addOrderForm.city_B.data)
    cursor.execute(
        "INSERT INTO orders(id_order, id_driver, id_client, id_product, weight, datedelivery, is_delivery, point_a, point_b) "
        "VALUES ((SELECT MAX(id_order) + 1 FROM orders),'{id_driver}','{id_client}', '{id_product}', '{weight}', '{datedelivery}', {is_delivery}, '{pointa}', '{pointb}')".format(
            id_driver = list_id['driver_id'], id_client = list_id['client_id'], id_product = list_id['product_id'], weight = list_id['weight'], datedelivery = list_id['date_delivery'], is_delivery = list_id['status'], pointa = list_id['city_A'], pointb = list_id['city_B'])
        )
    conn.commit()

def update_clientData(addClientForm):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client")
    clients = cursor.fetchall()
    flag = True
    for client in clients:
        if client[1] == addClientForm.client_name.data and client[2] == addClientForm.client_telephone.data and client[3] == addClientForm.client_card.data:
            flag = False
    if flag:
        cursor.execute("INSERT INTO client(id_client, nameofclient, telephone, cardnum) VALUES ((SELECT MAX(id_client) + 1 FROM client), '{nameofclient}', '{telephone}', {cardnum})".format(nameofclient = addClientForm.client_name.data, telephone = addClientForm.client_telephone.data, cardnum = addClientForm.client_card.data) )
        conn.commit()

def fromStrToID(driverStr, clientStr, productStr, weight, dateDelStr, statusStr, cityA_Str, cityB_Str):
    list_id = {}
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM driver WHERE username = '{}'".format(driverStr))
    driver_id = cursor.fetchone()
    list_id['driver_id'] = driver_id[0]
    cursor.execute("SELECT id_client FROM client WHERE nameofclient = '{}'".format(clientStr))
    client_id = cursor.fetchone()
    list_id['client_id'] = client_id[0]
    list_id['city_A'] = cityA_Str
    list_id['city_B'] = cityB_Str
    if (statusStr == 'Доставлен'):
        list_id['status'] = True
    elif (statusStr == 'Не доставлен'):
        list_id['status'] = False
    list_id['date_delivery'] = dateDelStr
    list_id['weight'] = float(weight)
    cursor.execute("SELECT id_product FROM product WHERE nameofproduct = '{}'".format(productStr))
    product_id = cursor.fetchone()
    if product_id == None:
        cursor.execute("INSERT INTO product(id_product, nameofproduct) VALUES ((SELECT MAX(id_product) + 1 FROM product),'{name_product}')".format(name_product = productStr))
        conn.commit()
        cursor.execute("SELECT id_product FROM product WHERE nameofproduct = '{}'".format(productStr))
        product_id = cursor.fetchone()
    list_id['product_id'] = product_id[0]
    return list_id


def createListDriver(driverList):
    listDriver = []
    for driver in driverList:
        if driver[2] != current_user.username:
            dictDriver = {'username': driver[2], 'name': driver[4], 'surname': driver[1], 'experiense': driver[5],
                          'datebirth': driver[7], 'car_number': get_carNum_by_id(driver[6]), 'car_model': get_carModel_by_id(driver[6])}
            listDriver.append(dictDriver)
    return listDriver

def createListOrder(orderList):
    listOrder = []
    for order in orderList:
        dictOrder = {'driver_name': get_driverName_by_id(order[1]), 'product': get_product_by_id(order[3]), 'client': get_clientName_by_id(order[2]), 'weight': order[4],
                          'date_delivery': time(order[5]), 'is_delivery': get_isDelivety_by_id(order[6]), 'point_A': order[7], 'point_B': order[8], 'num': order[0]}
        listOrder.append(dictOrder)
    return listOrder

def time(time):
    time = str(time)
    return time[0:10]

def get_carNum_by_id(id_car):
    if id_car is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT carnumber FROM car WHERE id_car = '{}'".format(id_car))
        car_number = cursor.fetchone()
        return car_number[0]

def get_carModel_by_id(id_car):
    if id_car is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT carname FROM car WHERE id_car = '{}'".format(id_car))
        car_model = cursor.fetchone()
        return car_model[0]

def get_driverName_by_id(id_driver):
    if id_driver is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM driver WHERE id = '{}'".format(id_driver))
        driver_name = cursor.fetchone()
        return driver_name[0]

def get_product_by_id(id_product):
    if id_product is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT nameofproduct FROM product WHERE id_product = '{}'".format(id_product))
        product_name = cursor.fetchone()
        return product_name[0]

def get_clientName_by_id(id_client):
    if id_client is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT nameofclient FROM client WHERE id_client = '{}'".format(id_client))
        client_name = cursor.fetchone()
        return client_name[0]

def get_isDelivety_by_id(is_delivery):
    if is_delivery == True:
        return 'Доставлен'
    elif is_delivery == False:
        return 'Не доставлен'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_form = LoginForm()
    print(login_form.username.data)
    print('passw = {}'.format(login_form.password.data))
    if login_form.validate_on_submit():
        print('BBBBB')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM driver ")
        driverData = cursor.fetchall()
        username = login_form.username.data
        password = login_form.password.data
        for data in driverData:
            if data[2] == username and data[3] == password:
                user = User(data[0])
                login_user(user, remember=login_form.remember_me.data)
                next_page = request.args.get('next')
                print(user.isadmin)
                if user.isadmin:
                    return redirect(url_for('admin_panel', username=user.username))
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
    return render_template('login.html', title='Sign In', form=login_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO driver(id, username, _password) VALUES ((SELECT MAX(id) + 1 FROM driver),'{}','{}')".format(
                form.username.data, form.password.data
            ))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM driver")
    usernameList = cursor.fetchall()
    driver_orders = createDict_orders(username)
    succedOrder = calculate_Order_forDriver(username, 'succed')
    inWorkOrder = calculate_Order_forDriver(username, 'work')
    for _username in usernameList:
        if _username[0] == username:
            cursor.execute("SELECT id FROM driver WHERE username = '{}'".format(username))
            id = cursor.fetchone()
            user = User(id[0])
            edit_form = EditProfileForm()
            if edit_form.validate_on_submit():
                update_userData(username, edit_form)
            return render_template('user.html', user=user, form=edit_form, orders = driver_orders, succedOrder = succedOrder, inWorkOrder = inWorkOrder)
    return render_template('404.html'), 404

def createDict_orders(username):
    listOrders = []
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM driver WHERE username = '{}'".format(username))
    id = cursor.fetchone()
    cursor.execute("SELECT * FROM orders WHERE id_driver = '{}'".format(id[0]))
    ordersList = cursor.fetchall()
    for order in ordersList:
        dictOrders = {'product':get_product_by_id(order[3]), 'weight': order[4], 'date_delivery': time(order[5]), 'is_delivery': get_isDelivety_by_id(order[6]), 'point_A': order[7], 'point_B': order[8]}
        listOrders.append(dictOrders)
    return listOrders

def calculate_Order_forDriver(username, status):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM driver WHERE username = '{}'".format(username))
    id = cursor.fetchone()
    if status == 'work':
        cursor = conn.cursor()
        cursor.execute("SELECT count(id_order) FROM orders WHERE is_delivery = false and id_driver = {}".format(id[0]))
        answer = cursor.fetchone()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT count(id_order) FROM orders WHERE is_delivery = true and id_driver = {}".format(id[0]))
        answer = cursor.fetchone()
    return answer[0]



def update_userData(username, edit_form):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM driver WHERE username = '{}'".format(username))
    id_user = cursor.fetchone()
    cursor.execute("UPDATE driver SET username = '{username}', surname = '{surname}', "
                   "namedriver = '{namedriver}', datebirth = '{datebirth}', "
                   "_password = '{password}' WHERE id ={id}".format(username=edit_form.username.data,
                                                                    surname=edit_form.surname.data,
                                                                    namedriver=edit_form.name.data,
                                                                    id=id_user[0],
                                                                    datebirth=parserDateStr(edit_form.datebirth.data),
                                                                    password = edit_form.password.data
                                                                    ))
    conn.commit()



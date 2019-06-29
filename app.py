import sqlite3
import os
from flask import Flask
from flask import request
from flask_cors import CORS
import json
import random
import uuid
import urllib
import requests

from twilio.rest import Client


app = Flask(__name__)
CORS(app)


USER_ID = "1"


def get_cursor():
    connection = sqlite3.connect("database.db")
    c = connection.cursor()
    return c


def init_db():
    c = get_cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS meals(
        id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
        title text,
        available integer,
        picture text,
        price real,
        category integer
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS promocodes(
        id integer PRIMARY KEY,
        code text,
        discount real
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id integer PRIMARY KEY,
        promocode text
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS workhours(
        opens text,
        closes text
    )
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (1, "stepik", 25.0)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (2, "delivery", 10.0)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (3, "doubletrouble", 50.0)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (4, "illbeback", 25.0)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (5, "libertyordeath", 100.0)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (6, "summer", 10.0)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (7, "pleaselpease", 5.0)
    """)

    c.execute("""
    INSERT INTO users VALUES (1, null)
    """)

    c.connection.commit()
    c.connection.close()


def fill_database():
    api_key = "3f2ee35f02fdaf80453bfb0ffc81aba6"
    key_words = "cake"
    c = get_cursor()

    for page in range (1, 4):
        params = {"key": api_key, "q": key_words, 'page': page}
        url_string = 'https://www.food2fork.com/api/search?' + urllib.parse.urlencode(params)
        r = requests.get(url_string)
        data = r.json()
        for item in data['recipes']:
            c.execute("""
            INSERT INTO meals (title, available, picture, price, category) VALUES (?, ?, ?, ?, ?)
            """, [
                item['title'],
                1,
                item['image_url'],
                item['social_rank'] + random.randint(0, 100),
                1
            ])
            c.connection.commit()
    c.connection.close()


def read_file(filename):
    opened_file = open(filename, 'r')
    config_content = opened_file.read()
    data = json.loads(config_content)
    opened_file.close()
    return data


def write_file(filename, data):
    opened_file = open(filename, 'w')
    opened_file.write(json.dumps(data))
    opened_file.close()



@app.route("/")
def hello():
    return "Hello"


@app.route("/alive")
def alive():
    data = read_file('config.json')

    return json.dumps({"alive": data['alive']})


@app.route("/workhours")
def workhours():
    data = read_file('config.json')

    return json.dumps(data['workhours'])



@app.route("/promotion")
def promotion():
    promotion_number = random.randint(0, 2)
    promotions = read_file('promotions.json')
    return json.dumps(promotions[promotion_number], ensure_ascii=False)


@app.route("/promo/<code>")
def checkpromo(code):
    c = get_cursor()
    c.execute("""
    SELECT * FROM promocodes WHERE code = ?
    """, [code])
    result = c.fetchone()
    if result is None:
        return json.dumps({'valid': False})

    promo_id, promo_code, promo_discount = result
    c.execute("""
    UPDATE users
    SET promocode = ?
    WHERE id = ?
    """, (promo_code, int(USER_ID)))
    c.connection.commit()
    c.connection.close()
    return json.dumps({'valid': True, "discount": promo_discount})


@app.route("/meals")
def meals_route():
    c = get_cursor()

    c.execute("""
    SELECT discount
    FROM promocodes
    WHERE code = (
        SELECT promocode
        FROM users
        WHERE ID = ?   
    )    
    """, (int(USER_ID),))
    result = c.fetchone()

    discount = 0
    if result is not None:
        discount = result[0]

    meals = []
    for meals_info in c.execute("""SELECT * FROM meals"""):
        meals_id, title, available, picture, price, category = meals_info
        meals.append({
            'id': meals_id,
            'title': title,
            'available': bool(available),
            'picture': picture,
            'price': price * (1.0 - discount/100),
            'category': category
        })
    return json.dumps(meals)


@app.route("/orders", methods = ["GET", "POST"])
def orders():
    if request.method == "GET":
        orders_data = read_file('orders.json')
        user_orders = []
        for order_id in orders_data:
            if orders_data[order_id]["user_id"] == USER_ID:
                user_orders.append(orders_data[order_id])
        return json.dumps(user_orders)
    elif request.method == "POST":
        raw_data = request.data.decode('utf-8')
        data = json.loads(raw_data)


        discount = 0
        users_data = read_file('users.json')
        promocode = users_data[USER_ID]["promocode"]
        if promocode != None:
            promocodes = read_file('promo.json')
            for p in promocodes:
                if p['code'] == promocode:
                    discount = p['discount']

        summ = 0
        meals = read_file('meal.json')
        for meal in meals:
            meal_id = meal['id']
            for user_meal_id in data['meals']:
                if user_meal_id == meal_id:
                    summ = summ + meal['price'] * (1.0 - discount/100)
                break

        new_order_id = str(uuid.uuid4())
        new_order = {
            "id": new_order_id,
            "meals": data['meals'],
            "summ": summ,
            "status": "accepted",
            "user_id": USER_ID
        }

        order_data = read_file('orders.json')
        order_data[new_order_id] = new_order
        write_file('orders.json', order_data)

        return json.dumps({'order_id': new_order_id, "status": new_order['status']})



@app.route("/notification")
def notif():
    sms_client = Client(
        "ACdde47e05e1dbd50be661f7b96fd0a414",
        "ce7fca4a6cd8211d2d84ef849138795a"
    )

    message = sms_client.messages.create(
        body = "New order is accepted",
        from_ = "+1858281020(9)",
        to = "+79045181316"
    )

    return json.dumps({"status": True})


@app.route ("/activeorder")
def activeorders():
    orders_data = read_file('orders.json')
    user_orders = []
    for order_id in orders_data:
        order = orders_data[order_id]
        if order["user_id"] == USER_ID and order['status'] == 'accepted':
            return json.dumps(order)
    return "", 404


@app.route("/orders/<order_id>", methods=["DELETE"])
def one_order(order_id):
    orders_data = read_file("orders.json")
    for saved_order_id in orders_data:
        order = orders_data[saved_order_id]
        if saved_order_id == order_id and order['user_id'] == USER_ID:
            orders_data[saved_order_id]['status'] = 'canseled'
            write_file('orders.json', orders_data)
            return json.dumps({'order_id': order_id, "status": "canseled"})
    return "", 404


if not os.path.exists("database.db"):
    init_db()
    fill_database()


app.run("0.0.0.0", 9000)

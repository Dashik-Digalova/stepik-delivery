from flask import Flask
from flask import request
from flask_cors import CORS
import json
import random
import uuid


app = Flask(__name__)
CORS(app)


USER_ID = "1"


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
    promocodes = read_file('promo.json')

    for promocode in promocodes:
        if promocode["code"] == code.lower():

            users_data = read_file('users.json')

            users_data[USER_ID]["promocode"] = code

            write_file('users.json', users_data)

            return json.dumps({"valid": True, "discount": promocode['discount']})
    return json.dumps({"valid": False})


@app.route("/meals")
def meals_route():
    meals = read_file('meal.json')

    users_data = read_file('users.json')

    discount = 0

    promocode = users_data[USER_ID]["promocode"]


    if promocode != None:
        promocodes = read_file('promo.json')

        for p in promocodes:
            if p ['code'] == promocode:
                discount = p['discount']

        for meal in meals:
            meal['price'] = (1.0 - discount/100) * meal['price']

    return json.dumps(meals)


@app.route("/orders", methods = ["GET", "POST"])
def orders():
    if request.method == "GET":
        pass
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
            "sum": summ,
            "status": "accepted",
            "user_id": USER_ID
        }

        order_data = read_file('orders.json')
        order_data[new_order_id] = new_order
        write_file('orders.json', order_data)

        return json.dumps({'order_id': new_order_id, "status": new_order['status']})

app.run("0.0.0.0", 8000)

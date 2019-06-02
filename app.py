from flask import Flask
import json
import random
app = Flask(__name__)

promotion_text = "Сегодня скидка 15% по промокоду stepik"

promocode = "stepik"


promocodes = [
    {"code": "stepik", "discount": 25},
    {"code": "delivery", "discount": 10},
    {"code": "doubletrouble", "discount": 50},
    {"code": "illbeback ", "discount": 25},
    {"code": "libertyordeath  ", "discount": 100},
    {"code": "summer", "discount": 10},
    {"code": "pleaselpease  ", "discount": 5}
]

meals = [{
 "title": "Chinken",
 "id": 1,
 "available": True,
 "picture": "",
 "price": 20.0,
 "category": 1
}, {
 "title": "Milk",
 "id": 2,
 "available": True,
 "picture": "",
 "price": 10.0,
 "category": 1
}]



@app.route("/")
def hello():
    return "Hello"


@app.route("/alive")
def alive():
    config_file = open('config.json', 'r')
    config_content = config_file.read()
    data = json.loads(config_content)
    config_file.close()

    return json.dumps({"alive": data['alive']})


@app.route("/workhours")
def workhours():
    config_file = open('config.json', 'r')
    config_content = config_file.read()
    data = json.loads(config_content)
    config_file.close()

    return json.dumps(data['workhours'])


@app.route("/promotion")
def promotion():
    promotion_number = random.randint(0, 2)
    promotion_file = open("promotions.json", "r")
    promotions = json.loads(promotion_file.read())
    return json.dumps(promotions[promotion_number], ensure_ascii=False)


@app.route("/promo/<codes>")
def checkpromo(codes):
    for promocode in promocodes:
        if promocode["code"] == codes.lower():
            return json.dumps({"valid": True, "discount": promocode['discount']})
    return json.dumps({"valid": False})


@app.route("/meals")
def meals_route():
    return json.dumps(meals)

app.run("0.0.0.0", 8000)

from flask import Flask
import random
app = Flask(__name__)


stepik_alive = True

workhours_opens = "10:00"
workhours_closes = "22:00"

promotion_text = "Сегодня скидка 15% по промокоду stepik"

promocode = "stepik"

promotions = [
    "Сегодня скидка 15% по промокоду stepik",
    "Сегодня скидка 10% по промокоду summer",
    "Удваиваем все пиццы по промокоду udodopizza"
]


@app.route("/")
def hello():
    return "Hello"


@app.route("/alive")
def alive():
    if stepik_alive == True:
        return '{"alive": true}'
    else:
        return '{"alive": false}'


@app.route("/workhours")
def workhours():
    return '{"opens": "'+ workhours_opens +'", "closes": "'+ workhours_closes +'"}'


@app.route("/promotion")
def promotion():
    promotion_number = random.randint(0, 2)
    return '{"promotion": "'+promotions[promotion_number]+'"}'


@app.route("/promo/<codes>")
def checkpromo(codes):
    if codes == 'promocode':
        return '{"valid":true, "discount": 15}'
    elif codes == 'summer':
        return '{"valid":true, "discount": 10}'
    elif codes == 'pleaseplease':
        return '{"valid":true, "discount": 5}'
    else:
        return '{"valid":false,"discount":0}'

app.run("0.0.0.0", 8000)

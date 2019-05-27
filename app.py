from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello"


@app.route("/alive")
def alive():
    return '{"alive": true}'


@app.route("/workhours")
def workhours():
    return '{"opens": "10:00", "closes": "22:00"}'


@app.route("/promotion")
def promotion_text():
    return '{"promotion": "Сегодня скидка 15% по промокоду stepik"}'


#@app.route("/promo/<stepik>")
#def checkpromo(stepik):
#    if stepik == 'stepik':
#        return '{"valid":true}'
#    else:
#        return '{"valid":false}'


@app.route("/promo/<codes>")
def checkpromo(codes):
    if codes == 'stepik':
        return '{"valid":true, "discount": 15}'
    elif codes == 'summer':
        return '{"valid":true, "discount": 10}'
    elif codes == 'pleaseplease':
        return '{"valid":true, "discount": 5}'
    else:
        return '{"valid":false,"discount":0}'

app.run("0.0.0.0", 8000)

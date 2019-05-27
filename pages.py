from flask import Flask
app = Flask(__name__)



@app.route("/workhours")
def workhours():
    return '{"opens": "10:00", "closes": "22:00"}'


@app.route("/promotion")
def promotion_text():
    return '{"promotion": "Сегодня скидка 15% по промокоду stepik"}'


@app.route("/promo/<stepik>")
def checkpromo(stepik):
    return '{"valid":true}'



app.run("0.0.0.0", 8000)
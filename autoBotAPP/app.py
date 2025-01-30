import os
import hashlib
import hmac
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

BOT_TOKEN = "7991701834:AAHFmqgqi4xq9NCn50dnlZfsOJ4OiJlxEgo"  # Укажи токен бота

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def check_auth(data):
    """ Проверка подлинности Telegram-авторизации """
    secret = hashlib.sha256(BOT_TOKEN.encode()).digest()
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"])
    h = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    return h == data["hash"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auth")
def auth():
    """ Обработка Telegram-авторизации """
    data = request.args.to_dict()
    if check_auth(data):
        return jsonify({"status": "ok", "user": data})
    return jsonify({"status": "error"}), 403

@app.route("/add_listing", methods=["POST"])
def add_listing():
    """ Обработка подачи объявления """
    brand = request.form["brand"]
    model = request.form["model"]
    price = request.form["price"]
    description = request.form["description"]
    photo = request.files["photo"]

    photo_path = None
    if photo:
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo.filename)
        photo.save(photo_path)

    return f"Объявление добавлено: {brand} {model}, {price} руб."

if __name__ == "__main__":
    app.run(debug=True)

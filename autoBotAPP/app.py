
import hashlib
import hmac
from flask import Flask, request, render_template, jsonify
import cloudinary
import cloudinary.uploader
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

app = Flask(__name__)

# Настройка Telegram Bot
BOT_TOKEN = "7991701834:AAHFmqgqi4xq9NCn50dnlZfsOJ4OiJlxEgo"  # Укажи токен бота
updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Настройка Cloudinary
cloudinary.config(
    cloud_name="dqrp0zgwp",
    api_key="172714946631956",
    api_secret="nNB6l6ov7r8tRphA27AqHtgn9rQ"
)

def start(update: Update, context: CallbackContext):
    """Начальная команда бота"""
    update.message.reply_text("Добро пожаловать! Для подачи объявления используйте команду /addlisting.")

def add_listing(update: Update, context: CallbackContext):
    """Команда для добавления объявления через Telegram"""
    update.message.reply_text("Пожалуйста, отправьте ваше объявление с фотографией.")

def handle_message(update: Update, context: CallbackContext):
    """Обработка сообщений (например, если пользователь отправит текст или фото)"""
    if update.message.photo:
        # Если есть фото, отправляем на Cloudinary
        photo = update.message.photo[-1].get_file()
        photo_url = photo.file_path  # Получаем URL фото
        
        update.message.reply_text(f"Фото добавлено: {photo_url}")
    else:
        update.message.reply_text("Пожалуйста, отправьте фото для вашего объявления.")

# Добавление обработчиков команд
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addlisting", add_listing))

# Обработка текста и фото
dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo, handle_message))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auth")
def auth():
    """Обработка Telegram-авторизации"""
    data = request.args.to_dict()
    if check_auth(data):
        return jsonify({"status": "ok", "user": data})
    return jsonify({"status": "error"}), 403

@app.route("/add_listing", methods=["POST"])
def add_listing():
    """Обработка подачи объявления"""
    brand = request.form["brand"]
    model = request.form["model"]
    price = request.form["price"]
    description = request.form["description"]
    photo = request.files["photo"]

    photo_url = None
    if photo:
        # Сохраняем фото на Cloudinary и получаем URL
        photo_url = upload_to_cloudinary(photo)

    return f"Объявление добавлено: {brand} {model}, {price} руб. Фото: {photo_url}"

if __name__ == "__main__":
    # Запуск Telegram-бота в отдельном потоке
    updater.start_polling()
    app.run(debug=True)

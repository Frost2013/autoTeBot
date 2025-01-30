
import hashlib
import hmac
from flask import Flask, request, render_template, jsonify
import cloudinary
import cloudinary.uploader
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import threading

app = Flask(__name__)

# Настройка Telegram Bot
BOT_TOKEN = "7991701834:AAHFmqgqi4xq9NCn50dnlZfsOJ4OiJlxEgo"  # Укажи токен бота

# Создание объекта Application
application = Application.builder().token(BOT_TOKEN).build()

# Настройка Cloudinary
cloudinary.config(
    cloud_name="dqrp0zgwp",
    api_key="172714946631956",
    api_secret="nNB6l6ov7r8tRphA27AqHtgn9rQ"
)

async def start(update: Update, context):
    """Начальная команда бота"""
    await update.message.reply_text("Добро пожаловать! Для подачи объявления используйте команду /addlisting.")

async def add_listing(update: Update, context):
    """Команда для добавления объявления через Telegram"""
    await update.message.reply_text("Пожалуйста, отправьте ваше объявление с фотографией.")

async def handle_message(update: Update, context):
    """Обработка сообщений (например, если пользователь отправит текст или фото)"""
    if update.message.photo:
        # Если есть фото, отправляем на Cloudinary
        photo = update.message.photo[-1].get_file()
        photo_url = photo.file_path  # Получаем URL фото
        await update.message.reply_text(f"Фото добавлено: {photo_url}")
    else:
        await update.message.reply_text("Пожалуйста, отправьте фото для вашего объявления.")

# Добавление обработчиков команд
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("addlisting", add_listing))

# Обработка текста и фото
application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

# Flask-обработчик
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

# Запуск Flask-сервера в отдельном потоке
def run_flask():
    app.run(debug=True, use_reloader=False)

# Запуск Telegram-бота в асинхронном режиме
def run_telegram_bot():
    application.run_polling()

if __name__ == "__main__":
    # Запуск Flask и Telegram-бота в отдельных потоках
    threading.Thread(target=run_flask).start()
    threading.Thread(target=run_telegram_bot).start()

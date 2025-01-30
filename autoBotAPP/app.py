import asyncio
import hashlib
import hmac
import logging
import cloudinary
import cloudinary.uploader
from flask import Flask, request, render_template, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import threading

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка Flask
app = Flask(__name__)

# Настройка Telegram Bot
BOT_TOKEN = "7991701834:AAHFmqgqi4xq9NCn50dnlZfsOJ4OiJlxEgo"  # Укажи токен бота

# Настройка Cloudinary
cloudinary.config(
    cloud_name="dqrp0zgwp",
    api_key="172714946631956",
    api_secret="nNB6l6ov7r8tRphA27AqHtgn9rQ"
)

# Инициализация Telegram-бота
async def start(update: Update, context: CallbackContext):
    """Команда /start"""
    logger.info(f"Received /start command from {update.message.chat_id}")
    await update.message.reply_text("Добро пожаловать! Для подачи объявления используйте команду /addlisting.")

async def add_listing(update: Update, context: CallbackContext):
    """Команда для добавления объявления через Telegram"""
    logger.info(f"Received /addlisting command from {update.message.chat_id}")
    await update.message.reply_text("Пожалуйста, отправьте ваше объявление с фотографией.")

async def handle_message(update: Update, context: CallbackContext):
    """Обработка сообщений (например, если пользователь отправит текст или фото)"""
    logger.info(f"Received message from {update.message.chat_id}: {update.message.text}")
    if update.message.photo:
        # Если есть фото, отправляем на Cloudinary
        photo = update.message.photo[-1].get_file()
        photo_url = photo.file_path  # Получаем URL фото
        logger.info(f"Uploaded photo URL: {photo_url}")
        await update.message.reply_text(f"Фото добавлено: {photo_url}")
    else:
        await update.message.reply_text("Пожалуйста, отправьте фото для вашего объявления.")

# Функция для запуска Telegram-бота
def run_telegram_bot():
    """Запуск Telegram-бота с командой /start"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addlisting", add_listing))

    # Обработка текста и фото
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    # Запуск Telegram-бота
    logger.info("Starting Telegram bot...")
    application.run_polling()

# Запуск Flask-сервера
@app.route("/")
def home():
    return render_template("index.html")

# Проверка подлинности для авторизации Telegram
def check_auth(data):
    """Проверка подлинности Telegram-авторизации"""
    secret = hashlib.sha256(BOT_TOKEN.encode()).digest()
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"])
    h = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    return h == data["hash"]

# Обработка Telegram-авторизации
@app.route("/auth")
def auth():
    """Обработка Telegram-авторизации"""
    data = request.args.to_dict()
    if check_auth(data):
        logger.info(f"User {data['id']} authenticated successfully.")
        return jsonify({"status": "ok", "user": data})
    else:
        logger.warning("Authentication failed.")
        return jsonify({"status": "error"}), 403

# Обработка подачи объявления через форму
@app.route("/add_listing", methods=["POST"])
def add_listing_form():
    """Обработка подачи объявления через форму"""
    brand = request.form["brand"]
    model = request.form["model"]
    price = request.form["price"]
    description = request.form["description"]
    photo = request.files["photo"]

    photo_url = None
    if photo:
        # Сохраняем фото на Cloudinary и получаем URL
        logger.info(f"Uploading photo for {brand} {model}...")
        photo_url = upload_to_cloudinary(photo)
        logger.info(f"Uploaded photo URL: {photo_url}")

    logger.info(f"Listing added: {brand} {model}, {price} руб.")
    return f"Объявление добавлено: {brand} {model}, {price} руб. Фото: {photo_url}"

# Функция для загрузки фото в Cloudinary
def upload_to_cloudinary(photo):
    """Загрузка фотографии на Cloudinary"""
    # Убедитесь, что фото передается корректно
    result = cloudinary.uploader.upload(photo)
    return result.get("url")

# Запуск Flask и Telegram-бота в одном процессе с использованием threading
if __name__ == "__main__":
    # Запускаем Flask сервер в отдельном потоке
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()

    # Запускаем Telegram-бота в основном потоке
    run_telegram_bot()

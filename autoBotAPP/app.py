import asyncio
import hashlib
import hmac
import logging
import cloudinary
import cloudinary.uploader
import tempfile
import threading
from flask import Flask, request, render_template, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка Flask
app = Flask(__name__)

# Настройка Telegram Bot
BOT_TOKEN = "7991701834:AAGup5Twe7glMvD30angplPtcy8_gDbHBJ0"  # Укажите ваш токен

# Настройка Cloudinary
cloudinary.config(
    cloud_name="dqrp0zgwp",
    api_key="172714946631956",
    api_secret="nNB6l6ov7r8tRphA27AqHtgn9rQ"
)

# Инициализация Telegram-бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    keyboard = [[
        InlineKeyboardButton("Подать объявление", callback_data="add_listing"),
        InlineKeyboardButton("Список объявлений", callback_data="listings")
    ], [
        InlineKeyboardButton("Поиск", callback_data="search")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    if query.data == "add_listing":
        await query.message.reply_text("Пожалуйста, отправьте ваше объявление с фотографией.")
    elif query.data == "listings":
        await query.message.reply_text("Здесь будут отображаться все объявления.")
    elif query.data == "search":
        await query.message.reply_text("Введите критерии поиска (например, марка, модель, цена).")

async def add_listing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления объявления через Telegram"""
    await update.message.reply_text("Пожалуйста, отправьте ваше объявление с фотографией.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений (например, если пользователь отправит текст или фото)"""
    if update.message.photo:
        photo = await update.message.photo[-1].get_file()
        photo_url = photo.file_path  # Получаем URL фото
        await update.message.reply_text(f"Фото добавлено: {photo_url}")
    else:
        await update.message.reply_text("Пожалуйста, отправьте фото для вашего объявления.")

# Функция для запуска Telegram-бота
async def run_telegram_bot():
    """Запуск Telegram-бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("addlisting", add_listing))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    
    await application.run_polling()

# Запуск Flask-сервера
@app.route("/")
def home():
    return render_template("index.html")

# Запуск Flask и Telegram-бота в отдельных потоках
if __name__ == "__main__":
    flask_thread = threading.Thread(target=lambda: app.run(debug=True, use_reloader=False))
    flask_thread.start()
    telegram_thread = threading.Thread(target=lambda: asyncio.run(run_telegram_bot()))
    telegram_thread.start()
    flask_thread.join()
    telegram_thread.join()

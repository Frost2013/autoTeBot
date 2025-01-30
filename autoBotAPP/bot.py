import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask, request, render_template
import os

# Установите свой токен бота
BOT_TOKEN = "7991701834:AAHFmqgqi4xq9NCn50dnlZfsOJ4OiJlxEgo"

# Инициализация Flask
app = Flask(__name__)

# Функция, которая будет запускаться при команде /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Добро пожаловать! Я бот для подачи объявлений о продаже автомобилей. Введите /add для подачи объявления.")

# Функция для обработки команд
def add_listing(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Отправьте мне информацию об автомобиле в формате: марка, модель, цена, описание.")

# Функция для обработки текстовых сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text

    if "марка" in user_message and "модель" in user_message and "цена" in user_message:
        update.message.reply_text(f"Ваше объявление:\n{user_message}\nДобавлено успешно!")
    else:
        update.message.reply_text("Не могу распознать ваше сообщение. Попробуйте снова.")

# Функция для запуска бота
def run_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_listing))

    # Обработчик сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запуск бота
    updater.start_polling()
    updater.idle()

# Маршрут для главной страницы
@app.route("/")
def home():
    return render_template("index.html")

# Запуск Flask приложения
if __name__ == "__main__":
    from threading import Thread
    thread = Thread(target=run_bot)
    thread.start()
    app.run(debug=True)

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Вставь сюда свой токен
TOKEN = "7991701834:AAHFmqgqi4xq9NCn50dnlZfsOJ4OiJlxEgo"
bot = telegram.Bot(token=TOKEN)

# Функция, которая будет отправлять ссылку на веб-приложение
def send_welcome(chat_id):
    keyboard = [
        [InlineKeyboardButton("Перейти в приложение", url="http://your-server-url.com")]  # Укажи свой URL сервера
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id, text="Нажми на кнопку, чтобы открыть приложение", reply_markup=reply_markup)

# Запуск бота
def start(update, context):
    chat_id = update.message.chat_id
    send_welcome(chat_id)

# Конфигурация для работы бота
from telegram.ext import Updater, CommandHandler

updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))

updater.start_polling()
updater.idle()

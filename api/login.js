import os
from telegram import Bot
from telegram.ext import Application
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Функция для Vercel (обработчик HTTP-запросов)
def handler(request):
    try:
        logger.info("Received request on /api/check")
        
        # Инициализация бота
        bot = Bot(token=TOKEN)
        
        # Отправка тестового сообщения в чат
        bot.send_message(chat_id=CHAT_ID, text="Server is running! 🚀")
        
        return {
            "statusCode": 200,
            "body": "Request processed successfully!"
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": f"Error: {e}"
        }
import os
import logging
from telegram import Bot
from bot import check_feeds

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Проверка переменных окружения
if not TOKEN or not CHAT_ID:
    logger.error("Missing TOKEN or CHAT_ID environment variables")
    raise ValueError("Missing TOKEN or CHAT_ID environment variables")

# Функция для Vercel (обработчик HTTP-запросов)
def handler(request):
    try:
        logger.info("Received request on /api/check")
        
        # Вызов check_feeds (синхронный)
        check_feeds()
        
        # Инициализация бота
        bot = Bot(token=TOKEN)
        
        # Отправка тестового сообщения в чат (синхронно)
        # Примечание: bot.send_message в python-telegram-bot v20.8 является асинхронным,
        # но мы можем использовать синхронный метод через run_sync
        bot._bot.send_message(chat_id=CHAT_ID, text="Server is running! 🚀")
        
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
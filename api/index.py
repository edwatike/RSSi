import os
import asyncio
from telegram import Bot
import logging
from bot import check_feeds

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Функция для Vercel (обработчик HTTP-запросов)
async def handler(request):
    try:
        logger.info("Received request on /api/check")
        
        # Вызов check_feeds
        check_feeds()
        
        # Инициализация бота
        bot = Bot(token=TOKEN)
        
        # Отправка тестового сообщения в чат (асинхронно)
        await bot.send_message(chat_id=CHAT_ID, text="Server is running! 🚀")
        
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

# Vercel требует синхронный обработчик, поэтому оборачиваем асинхронный код
def sync_handler(request):
    return asyncio.run(handler(request))
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram.ext import Application
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен бота (из твоего vercel.json)
TOKEN = "7763394832:AAFzvdwFrxtzfVeaJMwCDvsoD0JmYZ7Tkqo"

# Функция для проверки лент (заглушка, замени на свою логику)
def check_feeds():
    logger.info("check_feeds started")
    try:
        # Здесь должна быть твоя логика для проверки лент
        # Например, запрос к API, обработка данных и отправка в Telegram
        logger.info("Processing feeds...")
        # Пример: просто логируем текущую дату
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Current time: {current_time}")
    except Exception as e:
        logger.error(f"Error in check_feeds: {e}")
    finally:
        logger.info("check_feeds finished")

# Основная функция для запуска бота
def main():
    # Инициализация бота
    logger.info("Initializing bot...")
    app = Application.builder().token(TOKEN).build()

    # Удаление вебхука (если он был установлен)
    logger.info("Removing webhook...")
    app.bot.delete_webhook()

    # Инициализация планировщика
    logger.info("Setting up scheduler...")
    scheduler = BlockingScheduler()

    # Добавление задачи check_feeds с интервалом 10 секунд (для теста)
    scheduler.add_job(check_feeds, 'interval', seconds=10)

    # Запуск планировщика
    logger.info("Starting scheduler...")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    main()
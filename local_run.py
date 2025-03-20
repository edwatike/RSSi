import logging
import asyncio
import requests
import feedparser
import os
import re
from telegram.ext import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройки сервера
SERVER_URL = 'https://rssbot-server.vercel.app'  # Замените на ваш URL после деплоя
SERVER_USERNAME = 'admin'
SERVER_PASSWORD = 'yourpassword123'

# Список RSS-лент для проверки
RSS_FEEDS = [
    'https://towardsdatascience.com/feed',
    'https://venturebeat.com/feed/',
    'https://rss.app/feeds/PNcbNOcr3uiLMKOm.xml'
]

# Функция для очистки имени файла
def clean_filename(filename):
    # Удаляем недопустимые символы для имени файла
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Функция для загрузки файла на сервер
def upload_to_server(file_path, filename):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.post(
                f"{SERVER_URL}/upload",
                files=files,
                auth=(SERVER_USERNAME, SERVER_PASSWORD)
            )
        if response.status_code == 200:
            logger.info(f"File {filename} uploaded successfully")
            return True
        else:
            logger.error(f"Failed to upload {filename}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error uploading {filename}: {e}")
        return False

# Функция для проверки RSS-лент
async def check_feeds(context):
    logger.info("check_feeds started")
    logger.info("Processing feeds...")
    current_time = context.job_context['time']()
    logger.info(f"Current time: {current_time}")

    try:
        for feed_url in RSS_FEEDS:
            logger.info(f"Checking feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            if feed.bozo:
                logger.error(f"Failed to parse feed {feed_url}: {feed.bozo_exception}")
                continue

            for entry in feed.entries:
                # Извлечение заголовка и содержимого статьи
                title = entry.get('title', 'No title')
                content = entry.get('summary', entry.get('description', 'No content'))
                # Очистка имени файла
                clean_title = clean_filename(title)
                filename = f"{clean_title}_{int(current_time)}.txt"

                # Сохранение статьи в файл
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {title}\n\nContent: {content}")

                # Загрузка статьи на сервер
                if upload_to_server(filename, filename):
                    logger.info(f"Article {filename} uploaded to server")
                else:
                    logger.error(f"Failed to upload article {filename}")

                # Удаление локального файла после загрузки
                os.remove(filename)
    except Exception as e:
        logger.error(f"Error in check_feeds: {e}")

    logger.info("check_feeds finished")

# Основная функция для запуска бота
async def main():
    logger.info("Initializing bot...")

    # Инициализация бота
    # Замените "YOUR_BOT_TOKEN" на токен вашего бота от BotFather
    app = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Удаление вебхука (асинхронно)
    logger.info("Removing webhook...")
    await app.bot.delete_webhook(drop_pending_updates=True)

    # Настройка планировщика
    logger.info("Setting up scheduler...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_feeds,
        trigger=IntervalTrigger(seconds=10),
        context={'time': lambda: asyncio.get_event_loop().time()}
    )

    # Запуск планировщика
    logger.info("Starting scheduler...")
    scheduler.start()

    # Запуск бота в режиме polling
    logger.info("Starting bot polling...")
    await app.run_polling()

# Запуск асинхронного приложения
if __name__ == '__main__':
    asyncio.run(main())
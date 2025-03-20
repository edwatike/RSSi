import feedparser
import requests
import deepl
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from datetime import datetime

# Токен бота
BOT_TOKEN = "7763394832:AAFzvdwFrxtzfVeaJMwCDvsoD0JmYZ7Tkqo"

# API-ключ DeepL
DEEPL_API_KEY = "49a435b1-7380-4a48-bf9d-11b5db85f42b:fx"  # Замени на свой ключ

# Инициализация DeepL Translator
translator = deepl.Translator(DEEPL_API_KEY)

# URL сервера
SERVER_URL = "https://rssbot-server.onrender.com"
SERVER_USERNAME = "admin"
SERVER_PASSWORD = "yourpassword123"

# ID канала
CHANNEL_ID = "@noWnewnew"

# Папка для временного хранения файлов
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Список RSS-лент
RSS_FEEDS = [
    "https://towardsdatascience.com/feed",
    "https://venturebeat.com/feed/",
    "https://rss.app/feeds/PNcbNOcr3uiLMKOm.xml",
]

# Инициализация бота
app = Application.builder().token(BOT_TOKEN).build()

# Функция для проверки новых статей
async def check_feeds(bot):
    print("check_feeds started")
    for feed_url in RSS_FEEDS:
        print(f"Checking feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            # Используем дату публикации и заголовок для уникальности
            published = entry.get("published", entry.get("updated", ""))
            title = entry.get("title", "No title")
            summary = entry.get("summary", "No summary")
            link = entry.get("link", "")

            # Переводим заголовок и описание на русский
            try:
                translated_title = translator.translate_text(title, target_lang="RU").text
                translated_summary = translator.translate_text(summary, target_lang="RU").text
                translated_read_more = translator.translate_text("Read more", target_lang="RU").text
            except Exception as e:
                print(f"Translation error: {e}")
                translated_title = title  # Если перевод не удался, оставляем оригинал
                translated_summary = summary
                translated_read_more = "Read more"

            # Формируем имя файла на основе переведённого заголовка
            filename = f"{published}_{translated_title}.html".replace(" ", "_").replace(":", "-")
            
            # Проверяем, существует ли файл на сервере
            response = requests.head(
                f"{SERVER_URL}/articles/{filename}",
                auth=(SERVER_USERNAME, SERVER_PASSWORD)
            )
            if response.status_code == 200:
                continue  # Файл уже существует, пропускаем
            
            # Формируем содержимое переведённой статьи
            content = f"<h1>{translated_title}</h1>"
            content += f"<p>Published: {published}</p>"
            content += f"<p>{translated_summary}</p>"
            if link:
                content += f'<p><a href="{link}">{translated_read_more}</a></p>'
            
            # Сохраняем статью во временный файл
            temp_file_path = os.path.join(TEMP_DIR, filename)
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Загружаем статью на сервер
            with open(temp_file_path, "rb") as f:
                files = {"file": (filename, f, "text/html")}
                response = requests.post(
                    f"{SERVER_URL}/upload",
                    auth=(SERVER_USERNAME, SERVER_PASSWORD),
                    files=files
                )
            
            if response.status_code == 200:
                print(f"Article {filename} uploaded to server")
                # Формируем ссылку на статью
                article_url = f"{SERVER_URL}/articles/{filename}"
                message = f"Новая статья: {translated_title}\n{article_url}"
                # Отправляем сообщение в канал
                await bot.send_message(chat_id=CHANNEL_ID, text=message)
            else:
                print(f"Failed to upload {filename}: {response.text}")
            
            # Удаляем временный файл
            os.remove(temp_file_path)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running! It will check RSS feeds every 10 seconds and post updates to the channel.")

# Добавляем обработчик команды /start
app.add_handler(CommandHandler("start", start))

# Настройка планировщика
scheduler = AsyncIOScheduler()
scheduler.add_job(check_feeds, 'interval', seconds=10, args=[app.bot])
scheduler.start()

# Запуск бота
print("Bot is starting...")
app.run_polling()
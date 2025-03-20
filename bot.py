import logging
import feedparser
from telegram import Bot
from datetime import datetime
from utils import load_sent_entries, save_sent_entries, extract_media, is_after_start_date, translate_text, clean_html, fetch_article_content
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
START_DATE = os.getenv("START_DATE")
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Проверка переменных окружения
if not DEEPL_API_KEY or not START_DATE or not TOKEN or not CHAT_ID:
    logger.error("Missing required environment variables")
    raise ValueError("Missing required environment variables")

# Инициализация бота
bot = Bot(token=TOKEN)

# Список RSS-лент
RSS_FEEDS = [
    "https://towardsdatascience.com/feed",
    "https://venturebeat.com/feed/",
    "https://rss.app/feeds/PNcbNOcr3uiLMKOm.xml"
]

def check_feeds():
    logger.info("check_feeds started")
    try:
        # Загрузка уже отправленных записей (заглушка, так как Vercel не поддерживает постоянное хранение файлов)
        sent_entries = load_sent_entries()
        
        # Парсинг даты начала
        start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
        
        # Обработка каждой RSS-ленты
        for feed_url in RSS_FEEDS:
            logger.info(f"Parsing feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            # Проверка, успешно ли спарсена лента
            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_url}")
                continue
                
            logger.info(f"Parsed feed: {feed.feed.get('title', 'Unknown feed')}")
            
            for entry in feed.entries:
                # Получаем ID записи (или ссылку, если ID отсутствует)
                entry_id = entry.get("id", entry.link)
                if entry_id in sent_entries:
                    logger.info(f"Skipping already sent entry: {entry_id}")
                    continue
                
                # Проверка даты публикации
                try:
                    published = datetime(*entry.published_parsed[:6])
                except (AttributeError, TypeError) as e:
                    logger.warning(f"Could not parse published date for entry {entry_id}: {e}")
                    continue
                    
                if not is_after_start_date(published, start_date):
                    logger.info(f"Entry {entry_id} is before start date, skipping")
                    continue
                
                # Обработка записи
                title = clean_html(entry.title)
                translated_title = translate_text(title, DEEPL_API_KEY)
                logger.info(f"Translated title: {translated_title}")
                
                # Извлечение изображения (если есть)
                media_url = extract_media(entry.link)
                
                # Формирование сообщения
                message = f"New article: {translated_title}\nLink: {entry.link}"
                if media_url:
                    message += f"\nMedia: {media_url}"
                
                # Отправка сообщения в Telegram
                try:
                    bot._bot.send_message(chat_id=CHAT_ID, text=message)
                    logger.info(f"Sent message for entry: {entry_id}")
                except Exception as e:
                    logger.error(f"Failed to send message for entry {entry_id}: {e}")
                    continue
                
                # Добавляем запись в отправленные
                sent_entries.add(entry_id)
        
        # Сохраняем отправленные записи (заглушка, так как Vercel не поддерживает постоянное хранение файлов)
        save_sent_entries(sent_entries)
        
    except Exception as e:
        logger.error(f"Error in check_feeds: {e}")
    finally:
        logger.info("check_feeds finished")
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

def check_feeds():
    logger.info("check_feeds started")
    try:
        # Пример: парсинг RSS-ленты
        feed = feedparser.parse("https://example.com/feed")
        logger.info(f"Parsed feed: {feed.feed.title}")
        
        # Загрузка уже отправленных записей
        sent_entries = load_sent_entries()
        
        # Парсинг даты начала
        start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
        
        for entry in feed.entries:
            entry_id = entry.get("id", entry.link)
            if entry_id in sent_entries:
                continue
                
            published = datetime(*entry.published_parsed[:6])
            if not is_after_start_date(published, start_date):
                continue
                
            # Пример обработки записи
            title = clean_html(entry.title)
            translated_title = translate_text(title, DEEPL_API_KEY)
            logger.info(f"Translated title: {translated_title}")
            
            # Добавляем запись в отправленные
            sent_entries.add(entry_id)
        
        # Сохраняем отправленные записи
        save_sent_entries(sent_entries)
        
    except Exception as e:
        logger.error(f"Error in check_feeds: {e}")
    finally:
        logger.info("check_feeds finished")
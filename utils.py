import feedparser
import logging
import requests
from bs4 import BeautifulSoup
import pytz
import deepl
from datetime import datetime

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sent_entries():
    # Для Vercel используем временное хранилище или внешнее API
    # Здесь можно добавить интеграцию с Vercel KV или GitHub API
    # Для простоты пока оставим заглушку
    return set()

def save_sent_entries(sent_entries):
    # Для Vercel нужно использовать внешнее хранилище
    # Здесь можно добавить интеграцию с Vercel KV или GitHub API
    pass

def extract_media(entry):
    photo_url = None
    video_url = None
    if 'enclosures' in entry:
        for enclosure in entry.enclosures:
            if enclosure.get('type', '').startswith('image/'):
                photo_url = enclosure.get('url')
            elif enclosure.get('type', '').startswith('video/'):
                video_url = enclosure.get('url')
    if 'media_content' in entry:
        for media in entry.media_content:
            if media.get('medium') == 'image' or media.get('type', '').startswith('image/'):
                photo_url = media.get('url')
            elif media.get('medium') == 'video' or media.get('type', '').startswith('video/'):
                video_url = media.get('url')
    if not photo_url and 'summary' in entry:
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'):
            photo_url = img['src']
    return photo_url, video_url

def is_after_start_date(entry, start_date):
    if 'published_parsed' not in entry:
        logger.debug(f"Нет времени публикации для {entry.title}, считаем подходящей")
        return True
    pub_time = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC)
    logger.debug(f"Время публикации {entry.title}: {pub_time}")
    return pub_time >= start_date

def translate_text(text, api_key):
    try:
        translator = deepl.Translator(api_key)
        if len(text) > 5000:
            text = text[:5000] + "..."
        result = translator.translate_text(text, target_lang="RU")
        return result.text
    except Exception as e:
        logger.error(f"Ошибка перевода: {str(e)}")
        return text

def clean_html(html_text):
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    for tag in soup(['img', 'video', 'audio', 'script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return '\n'.join(lines)

def fetch_article_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()
        article = soup.find('article') or soup.find('div', class_='article-content') or soup.find('body')
        if article:
            text = article.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return '\n'.join(lines)
        else:
            logger.warning(f"Не удалось найти контент статьи: {url}")
            return ""
    except Exception as e:
        logger.error(f"Ошибка загрузки статьи {url}: {str(e)}")
        return ""
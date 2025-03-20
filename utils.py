import os
import requests
import deepl
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Пример функций (адаптируй под свои)
def load_sent_entries():
    # Временная заглушка, так как Vercel не поддерживает постоянное хранение файлов
    # В будущем замени на работу с базой данных
    return set()
    # try:
    #     with open("sent_entries.json", "r") as f:
    #         return set(json.load(f))
    # except FileNotFoundError:
    #     return set()

def save_sent_entries(entries):
    # Временная заглушка, так как Vercel не поддерживает постоянное хранение файлов
    # В будущем замени на работу с базой данных
    pass
    # with open("sent_entries.json", "w") as f:
    #     json.dump(list(entries), f)

def extract_media(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        img = soup.find("meta", property="og:image")
        return img["content"] if img else None
    except Exception as e:
        logger.error(f"Error extracting media: {e}")
        return None

def is_after_start_date(entry_date, start_date):
    return entry_date >= start_date

def translate_text(text, api_key):
    translator = deepl.Translator(api_key)
    result = translator.translate_text(text, target_lang="EN-US")
    return result.text

def clean_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text()

def fetch_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("article") or soup.find("div", class_="content")
        return article.get_text() if article else None
    except Exception as e:
        logger.error(f"Error fetching article content: {e}")
        return None
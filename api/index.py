import os
from datetime import datetime
import pytz
from telegram import Bot
from telegram.ext import Updater
from bot import check_feeds

def handler(request):
    token = os.getenv("TOKEN")
    chat_id = os.getenv("CHAT_ID")
    deepl_api_key = os.getenv("DEEPL_API_KEY")
    start_date_str = os.getenv("START_DATE")  # Формат: YYYY-MM-DD, например, 2025-03-19
    rss_feeds = [
        'https://towardsdatascience.com/feed',
        'https://venturebeat.com/feed/',
        'https://rss.app/feeds/PNcbNOcr3uiLMKOm.xml'
    ]

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    except ValueError:
        return {
            "statusCode": 400,
            "body": "Invalid START_DATE format. Use YYYY-MM-DD."
        }

    updater = Updater(token=token, use_context=True)
    context = updater.dispatcher
    context.job = type('Job', (), {})()
    context.job.data = {
        'start_date': start_date,
        'token': token,
        'chat_id': chat_id,
        'rss_feeds': rss_feeds,
        'deepl_api_key': deepl_api_key,
        'sent_entries': set()
    }

    check_feeds(context)

    return {
        "statusCode": 200,
        "body": "RSS feeds checked successfully."
    }
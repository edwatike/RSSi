import logging
import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler
import pytz
from datetime import datetime
import requests
import feedparser
# Исправленный импорт: абсолютный вместо относительного
from utils import load_sent_entries, save_sent_entries, extract_media, is_after_start_date, translate_text, clean_html, fetch_article_content

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_feeds(context):
    start_date = context.job.data['start_date']
    token = context.job.data['token']
    chat_id = context.job.data['chat_id']
    rss_feeds = context.job.data['rss_feeds']
    deepl_api_key = context.job.data['deepl_api_key']
    sent_entries = context.job.data['sent_entries']

    logger.info("Проверка RSS-лент началась")
    news_count = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for feed_url in rss_feeds:
        if news_count >= 5:
            break
        logger.info(f"Обрабатываю ленту: {feed_url}")
        try:
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            if feed.bozo:
                logger.error(f"Ошибка парсинга {feed_url}: {feed.bozo_exception}")
                continue
            logger.info(f"Найдено {len(feed.entries)} записей в ленте {feed_url}")
            for entry in feed.entries:
                if news_count >= 5:
                    break
                entry_id = entry.get('id', entry.link)
                if entry_id not in sent_entries and is_after_start_date(entry, start_date):
                    logger.info(f"Новая запись: {entry.title}")
                    title_ru = translate_text(entry.title, deepl_api_key)
                    content = entry.get('content', [{'value': ''}])[0]['value'] if 'content' in entry else entry.get('summary', '')
                    content_clean = clean_html(content)
                    content_ru = translate_text(content_clean, deepl_api_key) if content_clean else ""
                    article_text = fetch_article_content(entry.link)
                    article_text_ru = translate_text(article_text, deepl_api_key) if article_text else "Полный текст недоступен."
                    message = f"**{title_ru}**\n"
                    if content_ru:
                        message += f"{content_ru}\n\n"
                    message += f"Полный текст:\n{article_text_ru}"
                    if len(message) > 4096:
                        message = message[:4000] + "...\n\n[Читать дальше]({entry.link})"
                    photo_url, video_url = extract_media(entry)
                    try:
                        if video_url:
                            await context.bot.send_video(chat_id=chat_id, video=video_url, caption=message, parse_mode='Markdown')
                        elif photo_url:
                            await context.bot.send_photo(chat_id=chat_id, photo=photo_url, caption=message, parse_mode='Markdown')
                        else:
                            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
                        sent_entries.add(entry_id)
                        save_sent_entries(sent_entries)
                        news_count += 1
                        await asyncio.sleep(12)
                    except Exception as e:
                        logger.error(f"Ошибка отправки {title_ru}: {str(e)}")
                else:
                    logger.debug(f"Запись уже отправлена или раньше даты: {entry.title}")
        except Exception as e:
            logger.error(f"Ошибка обработки ленты {feed_url}: {str(e)}")
    logger.info(f"Проверка завершена, отправлено {news_count} новостей")

async def start(update, context):
    logger.info(f"Команда /start от {update.message.from_user.username}")
    await update.message.reply_text("Бот запущен! Новости будут отправляться в канал на русском языке.")

async def error_handler(update, context):
    logger.error(f"Ошибка: {context.error}")
    if isinstance(context.error, telegram.error.Conflict):
        logger.error("Конфликт: проверьте, что запущен только один бот.")
        raise context.error

def run_bot(token, chat_id, rss_feeds, deepl_api_key, start_date):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(error_handler)

    bot = Bot(token)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
    logger.info("Вебхук удалён")

    sent_entries = load_sent_entries()
    job_data = {
        'start_date': start_date,
        'token': token,
        'chat_id': chat_id,
        'rss_feeds': rss_feeds,
        'deepl_api_key': deepl_api_key,
        'sent_entries': sent_entries
    }

    app.job_queue.scheduler.configure(timezone=pytz.timezone('UTC'))
    app.job_queue.run_repeating(check_feeds, interval=600, first=0, data=job_data)

    loop.run_until_complete(app.initialize())
    loop.run_until_complete(app.start())
    loop.run_forever()
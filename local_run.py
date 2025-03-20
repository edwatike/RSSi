import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import logging
import threading
from datetime import datetime
import pytz
from bot import run_bot

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self._insert_text, msg)

    def _insert_text(self, msg):
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)

def setup_log_window():
    log_window = tk.Tk()
    log_window.title("Логи RSS-бота")
    log_window.geometry("600x400")
    log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, height=20, width=70)
    log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    log_handler = LogHandler(log_text)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_handler)
    return log_window

def get_start_date():
    current_year = datetime.now().year
    root = tk.Tk()
    root.withdraw()
    while True:
        date_input = simpledialog.askstring("Дата", "С какого месяца и дня смотреть новости? (Формат: ММ-ДД, например, 03-19):")
        if date_input is None:
            logger.info("Пользователь отменил ввод даты")
            return None
        try:
            start_date = datetime.strptime(f"{current_year}-{date_input}", '%Y-%m-%d')
            return start_date.replace(tzinfo=pytz.UTC)
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ММ-ДД (например, 03-19).")

def main():
    log_window = setup_log_window()

    token = '7763394832:AAFzvdwFrxtzfVeaJMwCDvsoD0JmYZ7Tkqo'
    chat_id = '-1002447054616'
    deepl_api_key = '49a435b1-7380-4a48-bf9d-11b5db85f42b:fx'
    rss_feeds = [
        'https://towardsdatascience.com/feed',
        'https://venturebeat.com/feed/',
        'https://rss.app/feeds/PNcbNOcr3uiLMKOm.xml'
    ]

    start_date = get_start_date()
    if start_date is None:
        log_window.destroy()
        return

    logger.info(f"Дата начала проверки: {start_date}")

    bot_thread = threading.Thread(target=run_bot, args=(token, chat_id, rss_feeds, deepl_api_key, start_date), daemon=True)
    bot_thread.start()

    log_window.mainloop()

if __name__ == '__main__':
    main()
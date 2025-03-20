import tkinter as tk
from tkinter import ttk
import pytz
from datetime import datetime
from bot import run_bot
import threading

class LogWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Логи бота")
        self.root.geometry("600x400")

        self.log_text = tk.Text(self.root, wrap=tk.WORD, height=20, width=70)
        self.log_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = self.scrollbar.set

    def append_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

class DateEntryWindow:
    def __init__(self, root, token, chat_id, rss_feeds, deepl_api_key, log_window):
        self.root = root
        self.root.title("Введите дату начала")
        self.root.geometry("300x150")
        self.token = token
        self.chat_id = chat_id
        self.rss_feeds = rss_feeds
        self.deepl_api_key = deepl_api_key
        self.log_window = log_window

        self.label = ttk.Label(self.root, text="Введите дату (ГГГГ-ММ-ДД):")
        self.label.pack(pady=10)

        self.date_entry = ttk.Entry(self.root)
        self.date_entry.pack(pady=5)
        self.date_entry.insert(0, "2025-03-19")

        self.submit_button = ttk.Button(self.root, text="Запустить бота", command=self.submit)
        self.submit_button.pack(pady=10)

    def submit(self):
        date_str = self.date_entry.get()
        try:
            start_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            self.log_window.append_log(f"Дата начала проверки: {start_date}")
            self.root.destroy()
            # Запускаем бота в главном потоке
            run_bot(self.token, self.chat_id, self.rss_feeds, self.deepl_api_key, start_date)
        except ValueError:
            self.log_window.append_log("Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД.")

def main():
    token = "7763394832:AAFzvdwFrxtzfVeaJMwCDvsoD0JmYZ7Tkqo"
    chat_id = "-1002447054616"
    deepl_api_key = "49a435b1-7380-4a48-bf9d-11b5db85f42b:fx"
    rss_feeds = [
        'https://towardsdatascience.com/feed',
        'https://venturebeat.com/feed/',
        'https://rss.app/feeds/PNcbNOcr3uiLMKOm.xml'
    ]

    # Создаем окно логов
    log_root = tk.Tk()
    log_window = LogWindow(log_root)

    # Создаем окно ввода даты
    date_root = tk.Toplevel(log_root)
    DateEntryWindow(date_root, token, chat_id, rss_feeds, deepl_api_key, log_window)

    # Запускаем GUI в главном потоке
    log_root.mainloop()

if __name__ == "__main__":
    main()
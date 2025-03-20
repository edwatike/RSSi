from flask import Flask, send_from_directory, request, abort
import os
from functools import wraps

app = Flask(__name__)

# Настройки базовой авторизации
USERNAME = "admin"
PASSWORD = "yourpassword123"  # Замените на свой пароль

# Папка для хранения статей
ARTICLES_DIR = "articles"
if not os.path.exists(ARTICLES_DIR):
    os.makedirs(ARTICLES_DIR)

# Функция для проверки авторизации
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            abort(401)  # Требуется авторизация
        return f(*args, **kwargs)
    return decorated

# Маршрут для отображения статей
@app.route('/articles/<path:filename>')
@require_auth
def serve_article(filename):
    return send_from_directory(ARTICLES_DIR, filename)

# Маршрут для загрузки статей (для бота)
@app.route('/upload', methods=['POST'])
@require_auth
def upload_article():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    filename = file.filename
    file.save(os.path.join(ARTICLES_DIR, filename))
    return "File uploaded successfully", 200

# Для Vercel важно, чтобы приложение было доступно как WSGI-приложение
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
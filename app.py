from flask import Flask, request, abort, send_from_directory, make_response
import os

app = Flask(__name__)

# Папка для хранения статей
ARTICLES_DIR = "articles"
os.makedirs(ARTICLES_DIR, exist_ok=True)

# Учётные данные для базовой авторизации
USERNAME = "admin"
PASSWORD = "yourpassword123"

# Проверка авторизации
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

# Функция для создания ответа 401 с заголовком WWW-Authenticate
def authenticate():
    return make_response(
        "The server could not verify that you are authorized to access the URL requested.", 
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

# Корневой маршрут
@app.route('/')
def index():
    return "Welcome to the RSS Bot Server! Articles are available at /articles/<filename>."

# Обработчик для загрузки статей
@app.route('/upload', methods=['POST'])
def upload_article():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    if 'file' not in request.files:
        abort(400, description="No file part")
    
    file = request.files['file']
    if file.filename == '':
        abort(400, description="No selected file")
    
    # Сохраняем файл в папку articles
    file_path = os.path.join(ARTICLES_DIR, file.filename)
    file.save(file_path)
    return {"message": f"Article {file.filename} uploaded successfully"}, 200

# Обработчик для получения статей
@app.route('/articles/<path:filename>')
def get_article(filename):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
    return send_from_directory(ARTICLES_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
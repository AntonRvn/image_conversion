from app import app  # Импортируем экземпляр app из __init__.py

@app.route('/')
def home():
    return "Hello World!"
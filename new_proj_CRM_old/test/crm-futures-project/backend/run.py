import os
from app import create_app, db
# from app.models import User # Раскомментируйте, если нужно работать с моделями здесь

# Загрузка переменных окружения из .env файла (Flask делает это автоматически, но для Gunicorn может быть полезно)
# from dotenv import load_dotenv
# load_dotenv()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Создание контекста приложения для работы с БД вне запросов (например, для миграций)
# app_context = app.app_context()
# app_context.push()

# Команды для CLI (можно добавить `flask db init/migrate/upgrade`)
@app.shell_context_processor
def make_shell_context():
    return dict(db=db) # Добавьте User=User и т.д.

if __name__ == '__main__':
    # Не используйте app.run() в продакшене с Gunicorn
    # app.run(host='0.0.0.0', debug=app.config['DEBUG'])
    pass # Gunicorn запустит приложение через run:app

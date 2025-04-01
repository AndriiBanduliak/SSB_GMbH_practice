import os
from app import create_app, db
from app.models import User, Contact # Убедимся, что модели импортированы для shell_context

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Команды для CLI
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Contact=Contact)

if __name__ == '__main__':
    # Для запуска без Docker (если нужно): app.run(host='0.0.0.0', debug=True)
    # В Docker будет запускаться через Gunicorn
    pass

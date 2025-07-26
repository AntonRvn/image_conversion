from celery import Celery
from flask import Flask
from app import app

celery = Celery(
    app.import_name,
    broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)
celery.conf.update(app.config)

# Для корректной работы задач с контекстом Flask
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask 
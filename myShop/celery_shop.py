import os

from celery import Celery

RABBITMQ_USERNAME = 'shop'
RABBITMQ_PASSWORD = 'shop'
RABBITMQ_HOST = '172.22.0.2'
RABBITMQ_PORT = 5672
BROKER_URl = f'amqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}'


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myShop.settings')

app = Celery('myshop', broker=BROKER_URl)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

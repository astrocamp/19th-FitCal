import os

from celery import Celery

# 設定 Django settings module 環境變數
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitcal.settings')

app = Celery('fitcal')

# 從 Django 設定讀取 Celery 設定（會抓以 CELERY_ 開頭的設定）
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動尋找 tasks.py 裡的任務
app.autodiscover_tasks()

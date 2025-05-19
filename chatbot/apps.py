import os
import threading
import time

import environ
from django.apps import AppConfig

from .fetcher import default_urls, fetch_and_save_if_updated


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return  # 避免重複執行（只在主進程執行）

        def delayed_update():
            time.sleep(3)  # ✅ 等待 Django 完全啟動再更新
            env = environ.Env()
            environ.Env.read_env()

            if env.bool('AUTO_UPDATE_KNOWLEDGE', default=False):
                print('Django 啟動完成，開始自動更新知識庫...')
                for name, url in default_urls().items():
                    try:
                        print(f'正在讀取：{url}')
                        fetch_and_save_if_updated(url, name)
                    except Exception as e:
                        print(f'無法更新 {name}：{e}')

        threading.Thread(target=delayed_update).start()

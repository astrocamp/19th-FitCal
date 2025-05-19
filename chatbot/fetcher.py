# 自動抓取每一個網頁頁面的資料，並轉換成文字檔，餵給智慧客服
import hashlib
import os

import environ
import requests
from bs4 import BeautifulSoup

# 載入環境變數（專案使用 django-environ）
env = environ.Env()
environ.Env.read_env()


def fetch_page_text(url):
    print(f'正在讀取：{url}')
    response = requests.get(url)
    if response.status_code != 200:
        print(f'請求失敗：HTTP {response.status_code}')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()

    return soup.get_text(separator='\n', strip=True)


def get_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def fetch_and_save_if_updated(url, filename, save_dir='chatbot/knowledge'):
    text = fetch_page_text(url)
    if text is None:
        return

    current_hash = get_hash(text)
    hash_path = os.path.join(save_dir, filename + '.hash')
    txt_path = os.path.join(save_dir, filename)

    os.makedirs(save_dir, exist_ok=True)

    last_hash = None
    if os.path.exists(hash_path):
        with open(hash_path, 'r') as f:
            last_hash = f.read().strip()

    if current_hash != last_hash:
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        with open(hash_path, 'w') as f:
            f.write(current_hash)
        print(f'內容已更新並儲存：{txt_path}')
    else:
        print(f'無變化：{filename} 保持不動')


# 之後要根據部署後的網址更改下方連結
def default_urls():
    return {
        'users.txt': 'http://127.0.0.1:8000/',
        'members.txt': 'http://127.0.0.1:8000/members/',
        'orders.txt': 'http://127.0.0.1:8000/orders/',
        'stores.txt': 'http://127.0.0.1:8000/stores/',
        'products.txt': 'http://127.0.0.1:8000/products/',
    }


if __name__ == '__main__':
    if env.bool('AUTO_UPDATE_KNOWLEDGE', default=False):
        for filename, url in default_urls().items():
            fetch_and_save_if_updated(url, filename)
    else:
        print('AUTO_UPDATE_KNOWLEDGE 未啟用，略過更新')

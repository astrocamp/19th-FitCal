import os

from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from products.models import Product
from stores.models import Store


# 從資料庫抓最新資料
def fetch_latest_store_product_info():
    stores = Store.objects.all()
    products = Product.objects.all()

    info = ''
    for store in stores:
        info += f'店家：{store.name}\n地址：{store.address}\n電話：{store.phone_number}\n營業時間：{store.opening_time}~{store.closing_time}\n'

    for product in products:
        info += f'所屬店家：{product.store}\n商品：{product.name}\n價格：{product.price}元\n卡路里：{product.calories}\n商品介紹：{product.description}\n現有庫存量：{product.quantity}'

    return info


# 處裡使用者的訊息
@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('message', '')
        reply = generate_chatbot_reply(user_input)
    return JsonResponse({'reply': reply})


# 設定AI助理
def generate_chatbot_reply(user_input):
    answer = fetch_latest_store_product_info()

    # 如果資料庫沒有找到答案，就用 OpenAI 輔助回答
    # 這會向 OpenAI 發送一個「聊天請求」，並回傳一個字典（Python 的 dict）
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                'role': 'system',
                'content': '你是一位溫柔有禮貌、善於解釋的網站客服助理，'
                '你的任務是根據以下提供的知識資料，協助使用者解答問題。\n\n'
                '請遵守以下規則：\n'
                '- 只能根據提供的知識資料作答\n'
                '- 不要依據常識、個人推測或未提供的背景知識作答\n'
                '- 不要補充或延伸未提及的內容\n\n'
                '若使用者的問題與知識資料無關，請回答：\n'
                '「這個問題目前無法提供進一步回應，建議您洽詢客服 fitcal@gmail.com。」\n\n'
                '請使用簡單、親切、易懂的語氣回答。\n\n'
                '以下是知識資料：\n' + answer,
            },
            {'role': 'user', 'content': user_input},
        ],
        temperature=0,  # 越低越不會亂發揮，只有0跟1的選項
    )
    # choices 是 OpenAI 回傳的 JSON 結構中固定會出現的欄位之一
    return response.choices[0].message.content  # 選擇第一個回答

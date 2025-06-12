import os

from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

import json

from django.db.models import Avg, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from products.models import Product
from stores.models import Rating, Store


# 從資料庫抓最新資料
def fetch_latest_store_product_info():
    # 預先抓出每間店對應的商品，避免 N+1 問題
    # 加上平均評分的註解
    stores = Store.objects.annotate(avg_rating=Avg('rating__score')).prefetch_related(
        Prefetch('products', queryset=Product.objects.all())
    )
    rating = Rating.objects.all()

    info = ''
    for store in stores:
        # 如果沒有評分，顯示為「尚無評分」
        rating_display = (
            f'{store.avg_rating:.1f} 分' if store.avg_rating else '尚無評分'
        )

        info += (
            f'店家：{store.name}\n'
            f'地址：{store.address}\n'
            f'電話：{store.phone_number}\n'
            f'營業時間：{store.opening_time}~{store.closing_time}\n'
            f'平均評分：{rating_display}\n\n'
        )

        for product in store.products.all():  # 不會重新查資料庫
            info += (
                f'所屬店家：{store.name}\n'
                f'商品：{product.name}\n'
                f'價格：{product.price}元\n'
                f'卡路里：{product.calories}\n'
                f'商品介紹：{product.description}\n'
                f'現有庫存量：{product.quantity}\n\n'
            )

    return info


# 處理使用者的訊息
@require_POST
def chatbot_api(request):
    data = json.loads(request.body)
    user_input = data.get('message', '')
    reply = generate_chatbot_reply(user_input)
    return JsonResponse({'reply': reply})


# 設定AI助理
def generate_chatbot_reply(user_input):
    answer = fetch_latest_store_product_info()

    response = client.chat.completions.create(
        model='gpt-4.1-nano-2025-04-14',
        messages=[
            {
                'role': 'system',
                'content': f"""你是一位溫柔有禮貌、善於解釋的網站客服助理，
                你的任務是根據以下提供的知識資料，協助使用者解答問題。
                請遵守以下規則：
                - 只能根據提供的知識資料作答
                - 不要依據常識、個人推測或未提供的背景知識作答
                - 不要補充或延伸未提及的內容
                - 若使用者的問題與知識資料無關，請回答：
                「這個問題目前無法提供進一步回應，建議您洽詢客服 fitcal@gmail.com。」
                - 若使用者尋求你的幫助，請回答：
                「我可以協助您尋找心儀的餐點，搭配卡路里資訊及評分狀況，解決你的選擇困難!」
                - 若使用者希望外送餐點，請回答：
                「目前平台沒有提供外送服務，您可以致電店家尋求進一步的協助!」
                - 若使用者希望加入LINE，請回答：
                「歡迎加入我們平台的LINE好友https://line.me/R/ti/p/@044ggaso，可以在LINE聊天室收到訂單最新資訊喔!」
                - 請使用簡單、親切、易懂的語氣回答。

                以下是知識資料：
                {answer}""",
            },
            {'role': 'user', 'content': user_input},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

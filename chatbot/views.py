import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ✅ 自動讀取 knowledge 資料夾所有 .txt 檔案
def load_knowledge():
    folder = os.path.join(os.path.dirname(__file__), 'knowledge')
    content = ''
    for filename in os.listdir(folder):
        if filename.endswith('.txt'):
            path = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content += f'\n\n### {filename.replace(".txt", "")}\n'
                content += f.read()
    return content.strip()


# 預先讀入所有知識
knowledge_text = load_knowledge()


@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')

            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            '你是一位溫柔有禮貌、善於解釋的網站客服助理。'
                            '請根據以下提供的知識資料協助使用者解答問題，'
                            '請盡量使用簡單、易懂、友善的語氣來回答。\n\n'
                            '如果問題與知識資料無關，請直接回應：\n'
                            '「這個問題我們目前無法提供進一步回應，建議您洽詢客服專線。」\n\n'
                            '以下是知識資料：\n' + knowledge_text
                        ),
                    },
                    {
                        'role': 'user',
                        'content': message,
                    },
                ],
            )

            reply = response.choices[0].message.content
            return JsonResponse({'reply': reply})

        except Exception as e:
            print('❌ 發生錯誤：', e)
            return JsonResponse({'reply': f'伺服器錯誤：{str(e)}'}, status=500)

    return JsonResponse({'error': '僅支援 POST 請求'}, status=405)

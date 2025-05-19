import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# 自動讀取 knowledge 資料夾所有 .txt 檔案
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
                            '你是一位溫柔有禮貌、善於解釋的網站客服助理，'
                            '你的任務是**根據以下提供的知識資料，協助使用者解答問題**。\n\n'
                            '如果問題與知識資料無關，請務必回答：\n'
                            '「這個問題目前無法提供進一步回應，'
                            '建議您洽詢客服 fitcal@gmail.com。」\n\n'
                            '請記住：\n'
                            '- 不要根據你自己的常識、推測或過去的訓練知識作答\n'
                            '- 不要補充資料，不要延伸解釋未提供的內容\n'
                            '- 僅能根據提供的內容回答\n\n'
                            '請使用簡單、親切、易懂的語氣回答問題。\n\n'
                            '以下是知識資料：\n' + knowledge_text
                        ),
                    },
                    {
                        'role': 'user',
                        'content': (
                            '請根據上方知識資料回答以下問題：\n\n'
                            f'{message}\n\n'
                            '如果無法從知識資料中找到明確答案，請不要猜測，'
                            '而是回應：「這個問題目前無法提供進一步回應，'
                            '建議您洽詢客服 fitcal@gmail.com。」'
                        ),
                    },
                ],
            )

            reply = response.choices[0].message.content
            return JsonResponse({'reply': reply})

        except Exception as e:
            print('發生錯誤：', e)
            return JsonResponse({'reply': f'伺服器錯誤：{str(e)}'}, status=500)

    return JsonResponse({'error': '僅支援 POST 請求'}, status=405)

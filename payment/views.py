import base64
import hashlib
import hmac
import json
import os
import uuid
from pathlib import Path

import environ
import requests
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


@csrf_exempt
def linepay_request(request):
    if request.method == 'POST':
        order_id = f'order_{str(uuid.uuid4())}'
        package_id = f'package_{str(uuid.uuid4())}'

        payload = {
            'amount': 100,
            'currency': 'TWD',
            'orderId': order_id,
            'packages': [
                {
                    'id': package_id,
                    'amount': 100,
                    'products': [
                        {
                            'id': '1',
                            'name': '測試商品',
                            'quantity': 1,
                            'price': 100,
                        }
                    ],
                }
            ],
            'redirectUrls': {
                'confirmUrl': request.build_absolute_uri(
                    reverse('payment:linepay_confirm')
                ),
                'cancelUrl': request.build_absolute_uri(
                    reverse('payment:linepay_cancel')
                ),
            },
        }

        signature_uri = env('LINE_SIGNATURE_REQUEST_URI')
        headers = create_headers(payload, signature_uri)

        body = json.dumps(payload)

        url = f'{env("LINE_SANDBOX_URL")}{env("LINE_REQUEST_URL")}'

        response = requests.post(url, headers=headers, data=body)

        if response.status_code == 200:
            data = response.json()
            if data['returnCode'] == '0000':
                return redirect(data['info']['paymentUrl']['web'])
            else:
                print(data['returnMessage'])
                return render(request, 'payment/checkout.html')
        else:
            print(f'Error: {response.status_code}')
            return render(request, 'payment/checkout.html')

    else:
        return render(request, 'payment/checkout.html')


def create_headers(body, uri):
    channel_id = env('LINE_CHANNEL_ID')
    nonce = str(uuid.uuid4())
    secret_key = env('LINE_CHANNEL_SECRET_KEY')
    body_to_json = json.dumps(body)
    message = secret_key + uri + body_to_json + nonce

    binary_message = message.encode()
    binary_secret_key = secret_key.encode()

    hash = hmac.new(binary_secret_key, binary_message, hashlib.sha256)

    signature = base64.b64encode(hash.digest()).decode()

    headers = {
        'Content-Type': 'application/json',
        'X-LINE-ChannelId': channel_id,
        'X-LINE-Authorization-Nonce': nonce,
        'X-LINE-Authorization': signature,
    }

    return headers


def linepay_confirm(request):
    transaction_id = request.GET.get('transactionId')

    if not transaction_id:
        return HttpResponse('Missing transaction ID', status=400)

    payload = {
        'amount': 100,
        'currency': 'TWD',
    }

    body = json.dumps(payload)
    signature_uri = f'/v3/payments/{transaction_id}/confirm'
    uri = f'{env("LINE_SANDBOX_URL")}{signature_uri}'
    headers = create_headers(payload, signature_uri)

    response = requests.post(uri, headers=headers, data=body)

    data = response.json()
    if data['returnCode'] == '0000':
        return render(request, 'payment/success.html')
    else:
        fail_message = data.get('returnMessage', 'Unknown error')
        print(data['returnMessage'])
        return render(request, 'payment/fail.html', {'message': fail_message})


def linepay_cancel(request):
    return render(request, 'payment/cancel.html')

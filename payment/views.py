import base64
import hashlib
import hmac
import json
import os
import uuid
from pathlib import Path

import environ
import requests
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from carts.models import Cart
from orders.models import Order, OrderItem, PendingOrder

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


@csrf_exempt
def linepay_request(request):
    pending_order_id = request.GET.get('pending_order_id')
    if not pending_order_id:
        messages.error(request, _('找不到訂單資訊'))
        return redirect('carts:index')

    pending_order = get_object_or_404(PendingOrder, id=pending_order_id)

    cart_id = request.GET.get('cart_id')
    cart = get_object_or_404(Cart, id=cart_id)
    if not cart:
        messages.error(request, _('找不到購物車資訊'))
        return redirect('carts:index')

    total_price = cart.total_price

    order_id = pending_order_id or str(uuid.uuid4())
    package_id = f'package_{str(uuid.uuid4())}'

    products = []
    for item in cart.items.all():
        products.append(
            {
                'id': str(item.product.id),
                'name': item.product.name,
                'quantity': item.quantity,
                'price': int(item.product.price),
            }
        )

    payload = {
        'amount': int(total_price),
        'currency': 'TWD',
        'orderId': order_id,
        'packages': [
            {
                'id': package_id,
                'amount': int(total_price),
                'products': products,
            }
        ],
        'redirectUrls': {
            'confirmUrl': request.build_absolute_uri(
                reverse('payment:linepay_confirm')
                + f'?pending_order_id={pending_order.id}&cart_id={cart.id}'
            ),
            'cancelUrl': request.build_absolute_uri(
                reverse('payment:linepay_cancel')
                + f'?pending_order_id={pending_order.id}&cart_id={cart.id}'
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
    pending_order_id = request.GET.get('pending_order_id')

    if not pending_order_id:
        messages.error(request, _('訂單資訊已過期'))
        return redirect('carts:index')

    pending_order = get_object_or_404(
        PendingOrder, id=pending_order_id, is_processed=False
    )

    cart_id = request.GET.get('cart_id')
    cart = get_object_or_404(Cart, id=cart_id)

    if not cart:
        messages.error(request, _('找不到購物車資訊'))
        return redirect('carts:index')

    total_price = cart.total_price

    if not transaction_id:
        return HttpResponse(_('缺少交易 ID'), status=400)

    payload = {
        'amount': int(total_price),
        'currency': 'TWD',
    }

    body = json.dumps(payload)
    signature_uri = f'/v3/payments/{transaction_id}/confirm'
    uri = f'{env("LINE_SANDBOX_URL")}{signature_uri}'
    headers = create_headers(payload, signature_uri)

    response = requests.post(uri, headers=headers, data=body)

    data = response.json()
    if data['returnCode'] == '0000':
        try:
            # 建立訂單
            with transaction.atomic():
                order = Order(
                    store=cart.store,
                    member=cart.member,
                    member_name=pending_order.member_name,
                    member_phone=pending_order.member_phone,
                    pickup_time=pending_order.pickup_time,
                    note=pending_order.note,
                    payment_status='PAID',
                    payment_method='LINE_PAY',
                    total_price=total_price,
                )

                for cart_item in cart.items.all():
                    # 建立訂單項目
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price,
                    )

                    # 更新庫存
                    cart_item.product.quantity -= cart_item.quantity
                    cart_item.product.save()

                # trigger signals with all items created
                order.save()

                # 標記 PendingOrder 為已處理
                pending_order.is_processed = True
                pending_order.save()

                # 刪除購物車
                cart.delete()

            messages.success(request, _('付款成功，訂單已建立'))
            return redirect('orders:show', id=order.id)

        except Exception as e:
            messages.error(request, _('建立訂單時發生錯誤：') + str(e))
            return render(request, 'payment/fail.html', {'message': _('建立訂單失敗')})

    else:
        fail_message = data.get('returnMessage', _('未知錯誤'))
        messages.error(request, _('付款失敗：') + str(fail_message))
        return render(request, 'payment/fail.html', {'message': fail_message})


def linepay_cancel(request):
    return render(request, 'payment/cancel.html')

import os
from datetime import timedelta
from pathlib import Path

import environ
import requests
from django.db import connection
from django.utils.timezone import localtime, now

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


def next_10min(datetime):
    """
    計算下一個 10 分鐘的時間點
    :param datetime: 當前時間
    :return: 下一個 10 分鐘的時間點
    :rtype: datetime

    :example:
    10:00 -> 10:10
    10:01 -> 10:20
    """
    datetime += timedelta(minutes=10)
    # 計算要補幾分鐘才會對齊下一個 10 分鐘點
    remainder = datetime.minute % 10
    if remainder != 0:
        datetime += timedelta(minutes=(10 - remainder))
    return datetime.replace(second=0, microsecond=0)


def get_order_number():
    date_str = localtime(now()).strftime('%Y%m%d')
    seq_name = f'order_seq_{date_str}'

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_class WHERE relname = %s
                ) THEN
                    CREATE SEQUENCE {seq_name} START 1;
                END IF;
            END
            $$;
        """,
            [seq_name],
        )

        cursor.execute(f"SELECT nextval('{seq_name}')")
        next_val = cursor.fetchone()[0]
        return f'ORD{date_str}{next_val:06d}'


def get_pickup_number(store_id):
    short_id = str(store_id).replace('-', '')[:8]
    date_str = localtime(now()).strftime('%Y%m%d')
    seq_name = f'pickup_seq_{short_id}_{date_str}'

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_class WHERE relname = %s
                ) THEN
                    CREATE SEQUENCE {seq_name} START 1;
                END IF;
            END
            $$;
        """,
            [seq_name],
        )

        cursor.execute(f"SELECT nextval('{seq_name}')")
        next_val = cursor.fetchone()[0]
        return f'{(next_val - 1) % 9999 + 1:04d}'


LINE_MESSAGING_CHANNEL_ACCESS_TOKEN = env('LINE_MESSAGING_CHANNEL_ACCESS_TOKEN')
LINE_PUSH_URL = env('LINE_PUSH_URL')


def push_line_message(line_user_id, message_text):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_MESSAGING_CHANNEL_ACCESS_TOKEN}',
    }

    data = {
        'to': line_user_id,
        'messages': [
            {
                'type': 'text',
                'text': message_text,
            }
        ],
    }

    response = requests.post(LINE_PUSH_URL, headers=headers, json=data)
    return response.json()


def build_line_order_message(order):
    lines = [
        f'✅ 您的訂單 #{order.order_number} 已建立，感謝使用 FitCal！',
        '',
        f'🏪 店家：{order.store_name}',
        f'📞 店家電話：{order.store_phone}',
        f'🔢 取餐號碼：{order.pickup_number}',
        f'📅 取餐時間：{order.pickup_time.strftime("%Y-%m-%d %H:%M")}',
        '',
        '📦 商品內容：',
    ]

    total = 0
    for item in order.orderitem_set.all():
        lines.append(
            f'- {item.product_name} x {item.quantity}（{item.unit_price} 元）= {item.subtotal:.0f} 元'
        )
        total += item.subtotal

    lines.append('')
    lines.append(f'💰 訂單總金額：{total:.0f} 元')

    return '\n'.join(lines)

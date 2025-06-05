from datetime import timedelta

from django.db import connection
from django.utils.timezone import localtime, now


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

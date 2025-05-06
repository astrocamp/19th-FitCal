from datetime import timedelta


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

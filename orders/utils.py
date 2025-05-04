# 預計取餐時間至少要在 10 分鐘後
def round_up_to_next_10min(dt):
    # 先計算向上取整到最近10分鐘的倍數
    next_slot = ((dt.minute + 9) // 10) * 10
    # 然後再推進一個10分鐘單位，確保是至少下一個10分鐘槽
    minute = next_slot + 10
    hour = dt.hour
    if minute >= 60:
        hour += 1
        minute -= 60
    return dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

from datetime import datetime

import pytest

from orders.utils import next_10min


@pytest.mark.parametrize(
    'input_time, expected_time',
    [
        # 測試整點情況
        (datetime(2025, 5, 6, 10, 0), datetime(2025, 5, 6, 10, 10)),
        # 測試非整點情況
        (datetime(2025, 5, 6, 10, 5), datetime(2025, 5, 6, 10, 20)),
        (datetime(2025, 5, 6, 10, 11), datetime(2025, 5, 6, 10, 30)),
        # 測試跨小時情況
        (datetime(2025, 5, 6, 10, 55), datetime(2025, 5, 6, 11, 10)),
        # 測試跨天情況
        (datetime(2025, 5, 6, 23, 55), datetime(2025, 5, 7, 0, 10)),
    ],
)
def test_next_10min(input_time, expected_time):
    """
    測試 next_10min 函數是否正確計算下一個 10 分鐘的時間點
    """
    result = next_10min(input_time)
    assert result == expected_time, (
        f'輸入時間: {input_time}, 預期: {expected_time}, 實際: {result}'
    )

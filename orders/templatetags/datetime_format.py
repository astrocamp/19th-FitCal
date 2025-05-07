from django import template
from django.utils.timezone import localtime

register = template.Library()


@register.filter
def datetime_format(value, format='%Y年%-m月%-d日 %H:%M'):
    """
    將 datetime 格式化為自訂格式。
    預設格式為：2025年5月7日 16:40
    """
    if not value:
        return ''
    # 如果是時間物件，轉換為當地時間
    local_value = localtime(value)

    return local_value.strftime(format)

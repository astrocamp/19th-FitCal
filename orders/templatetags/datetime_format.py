from django import template

register = template.Library()


@register.filter
def datetime_format(value, fmt='%Y年%-m月%-d日 %H:%M'):
    """
    將 datetime 格式化為自訂格式。
    預設格式為：2025年5月7日 16:40
    """
    if not value:
        return ''
    return value.strftime(fmt)

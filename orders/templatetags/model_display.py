from django import template

register = template.Library()


@register.filter
def get_display(obj, field_name):
    """
    取得 Model 某個 choices 欄位的 display 名稱。
    用法：{{ object|get_display:"status" }}
    等同於 object.get_status_display()
    """
    method = getattr(obj, f'get_{field_name}_display', None)
    if method and callable(method):
        return method()
    return getattr(obj, field_name, '')

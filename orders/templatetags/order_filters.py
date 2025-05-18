from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """將兩個數字相乘"""
    return value * arg

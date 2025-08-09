from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """
    Multiplies the value by the argument.
    Usage: {{ some_value|mul:another_value }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return '' # Or handle error appropriately

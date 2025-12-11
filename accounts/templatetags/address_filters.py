from django import template

register = template.Library()

@register.filter
def before_comma(value):
    if not value:
        return ""
    return value.split(",")[0].strip()

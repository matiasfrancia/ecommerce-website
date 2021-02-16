from django import template

register = template.Library()

@register.filter
def to_clp(value):
    money = '{:,}'.format(value)
    clp = money.replace(',','.')
    return clp

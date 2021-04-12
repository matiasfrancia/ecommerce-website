from django import template

register = template.Library()

@register.filter
def to_clp(value):
    money = '{:,}'.format(value)
    clp = money.replace(',','.')
    return clp

@register.filter
def date_to_numbers(date):
    print(date)
    line = str(date).split('-')
    line.reverse()
    date = '/'.join(line)
    return date

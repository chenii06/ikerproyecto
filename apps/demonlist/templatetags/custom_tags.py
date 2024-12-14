from django import template
import math

register = template.Library()

@register.filter(name='ceil')
def ceil(value):
    return math.ceil(float(value))

@register.filter(name='neg')
def neg(value):
    return int(-value)

@register.filter(name='sub')
def sub(value, arg):
    return int(value) - int(arg)

@register.filter(name='diff_string')
def diff_string(value):
    palabras = value.split()
    return palabras[0].lower() if palabras else ''

@register.filter(name='first_word')
def first_word(value):
    return value.split()[0]

@register.filter(name='second_word')
def second_word(value):
    return value.split()[1]

@register.filter(name='count_checked')
def count_checked(demons, record_demons):
    if record_demons:
        return sum(1 for demon in demons if demon.id in record_demons)
    else:
        return 0
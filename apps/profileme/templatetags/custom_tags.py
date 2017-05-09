# display choice when printing form values
from datetime import date
from django import template

register = template.Library()


# @register.filter
# def human_readable(value, arg):
#     if hasattr(value, 'get_' + str(arg) + '_display'):
#         return getattr(value, 'get_%s_display' % arg)()
#     elif hasattr(value, str(arg)):
#         if callable(getattr(value, str(arg))):
#             return getattr(value, arg)()
#         else:
#             return getattr(value, arg)
#     else:
#         try:
#             return value
#         except KeyError:
#             return settings.TEMPLATE_STRING_IF_INVALID

# register.filter('human_readable', human_readable)


# calculate age withour days, seconds etc.
@register.filter
def calculate_age(born):
    today = date.today()

    return oday.year - born.year - ((today.month, today.day) < (born.month, born.day))

register.filter('age', calculate_age)

@register.filter
def rupluralize(value, arg="muzhik,muzhika,muzhikov"):
    args = arg.split(",")
    number = abs(int(value))
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return args[0]
    elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
        return args[1]
    else:
        return args[2]
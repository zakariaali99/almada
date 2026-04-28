from django import template


register = template.Library()

ARABIC_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


@register.filter
def arabic_digits(value):
    return str(value).translate(ARABIC_DIGITS)

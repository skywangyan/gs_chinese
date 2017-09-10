from django import template
register = template.Library()

@register.filter
def getbyindex(List, i):
    return List[int(i)]

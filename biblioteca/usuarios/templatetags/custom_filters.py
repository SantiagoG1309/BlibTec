from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Agrega una clase CSS al widget del campo del formulario.
    """
    return value.as_widget(attrs={'class': arg})
from django import template

from .service import NOTION_SELECT_PROPERTIES

register = template.Library()


@register.simple_tag
def select_properties():
    return NOTION_SELECT_PROPERTIES

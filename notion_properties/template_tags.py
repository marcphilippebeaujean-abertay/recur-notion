from django import template

from pages.template_tags import bootstrap_icon_by_icon_name

register = template.Library()


@register.simple_tag
def icon_by_property_type(notion_type):
    icon_by_property_type = {
        "multi_select": "card-checklist",
        "select": "arrow-down-circle-fill",
        "email": "envelope",
        "phone_number": "telephone",
        "url": "link",
        "rich_text": "justify-left",
        "title": "fonts",
        "number": "hash",
        "checkbox": "check2-square",
    }
    return bootstrap_icon_by_icon_name(icon_by_property_type[notion_type])


# alarm

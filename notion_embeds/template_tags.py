from django import template

from pages.template_tags import bootstrap_icon_by_icon_name

register = template.Library()


@register.simple_tag
def icon_by_property_type(notion_type, height=16, width=16):
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
        "date": "calendar",
        "created_time": "calendar",
        "people": "calendar",
    }
    return bootstrap_icon_by_icon_name(
        icon_by_property_type[notion_type], height=height, width=width
    )


@register.simple_tag
def get_simple_name_by_property_type(notion_type):
    simple_name = {
        "multi_select": "Multi-Select",
        "select": "Select",
        "email": "E-Mail",
        "phone_number": "Phone Number",
        "url": "URL",
        "rich_text": "Text",
        "title": "Text",
        "number": "Number",
        "checkbox": "Checkbox",
        "date": "Date",
        "created_time": "Created Time",
        "people": "People",
    }
    return simple_name[notion_type]

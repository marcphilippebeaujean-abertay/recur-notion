from django import template

register = template.Library()


@register.simple_tag
def icon_by_property_type(notion_type):
    icon_by_property_type = {
        'multi_select': 'card-checklist',
        'select': 'arrow-down-circle-fill',
        'email': 'envelope',
        'phone_number': 'telephone',
        'url': 'link',
        'rich_text': 'justify-left',
        'title': 'fonts',
        'number': 'hash',
        'checkbox': 'check2-square'
    }
    return icon_by_property_type[notion_type]

#alarm
from django import template

from .models import RecurringTask

register = template.Library()


@register.simple_tag
def interval_choices():
    return RecurringTask.TaskIntervals.choices
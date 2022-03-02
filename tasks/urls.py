from django.urls import path

from .views import (
    create_recurring_task,
    delete_recurring_task,
    duplicate_recurring_task,
    get_recurring_tasks,
    recurring_task_view,
    recurring_tasks_view,
    update_recurring_task_database,
    update_recurring_task_properties,
    update_recurring_task_schedule,
)

urlpatterns = [
    path("create-recurring-task/", create_recurring_task, name="create-recurring-task"),
    path("get-recurring-tasks/", get_recurring_tasks, name="get-recurring-tasks"),
    path("recurring-task/<int:pk>", recurring_task_view, name="recurring-task-view"),
    path(
        "delete-recurring-task/<int:pk>",
        delete_recurring_task,
        name="delete-recurring-task",
    ),
    path(
        "duplicate-recurring-task/<int:pk>",
        duplicate_recurring_task,
        name="duplicate-recurring-task",
    ),
    path(
        "update-recurring-task-schedule/<int:pk>",
        update_recurring_task_schedule,
        name="update-recurring-task-schedule",
    ),
    path(
        "update-recurring-task-properties/<int:pk>",
        update_recurring_task_properties,
        name="update-recurring-task-properties",
    ),
    path(
        "update-recurring-task-database/<int:pk>",
        update_recurring_task_database,
        name="update-recurring-task-database",
    ),
    path("tasks", recurring_tasks_view, name="recurring-tasks-view"),
]

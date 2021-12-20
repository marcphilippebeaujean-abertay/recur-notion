from django.urls import path
from .views import recurring_tasks_view, create_recurring_task, delete_recurring_task, get_recurring_tasks_for_notion_task_id, get_notion_workspace_tasks, update_recurring_task


urlpatterns = [
    path('create-recurring-task/', create_recurring_task, name='create-recurring-task'),
    path('get-recurring-task/', get_recurring_tasks_for_notion_task_id, name='get-recurring-tasks'),
    path('delete-recurring-task/<int:pk>', delete_recurring_task, name='delete-recurring-task'),
    path('update-recurring-task/<int:pk>', update_recurring_task, name='update-recurring-task'),
    path('tasks', recurring_tasks_view, name='recurring-tasks-view'),
    path('get-notion-workspace-tasks/', get_notion_workspace_tasks, name='get-notion-workspace-tasks'),
]
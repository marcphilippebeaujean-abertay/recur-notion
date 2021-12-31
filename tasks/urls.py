from django.urls import path
from .views import recurring_tasks_view, create_recurring_task, delete_recurring_task, get_recurring_tasks, recurring_task_view, update_recurring_task


urlpatterns = [
    path('create-recurring-task/', create_recurring_task, name='create-recurring-task'),
    path('get-recurring-tasks/', get_recurring_tasks, name='get-recurring-tasks'),
    path('recurring-task/<int:pk>', recurring_task_view, name='recurring-task-view'),
    path('delete-recurring-task/<int:pk>', delete_recurring_task, name='delete-recurring-task'),
    path('update-recurring-task/<int:pk>', update_recurring_task, name='update-recurring-task'),
    path('tasks', recurring_tasks_view, name='recurring-tasks-view'),
]
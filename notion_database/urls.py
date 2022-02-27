from django.urls import path

from .views import search_workspace_databases_for_task_db_change

urlpatterns = [
    path(
        "search-workspace-databases-for-task-db-change/",
        search_workspace_databases_for_task_db_change,
        name="search-workspace-databases-for-task-db-change",
    ),
]

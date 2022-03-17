from django.urls import path

from .views import search_workspace_databases_for_notion_embed_db_change

urlpatterns = [
    path(
        "search-workspace-databases-for-notion-embed-change/",
        search_workspace_databases_for_notion_embed_db_change,
        name="search-workspace-databases-for-notion-embed-db-change",
    ),
]

from django.urls import path

from .views import add_notion_workspace_from_access_code, show_notion_access_prompt

urlpatterns = [
    path("notion-oauth", add_notion_workspace_from_access_code),
    path(
        "notion-access-prompt", show_notion_access_prompt, name="notion-access-prompt"
    ),
]

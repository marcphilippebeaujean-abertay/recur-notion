from django.urls import path

from .views import (
    create_notion_embed,
    delete_notion_embed,
    notion_embed_view,
    notion_embeds_list_view,
    update_notion_embed_database,
    update_notion_embed_name,
    update_notion_embed_properties_settings,
)

urlpatterns = [
    path("create-notion-embed/", create_notion_embed, name="create-notion-embed"),
    path("notion-embed/<int:pk>", notion_embed_view, name="notion-embed-view"),
    path(
        "delete-notion-embed/<int:pk>",
        delete_notion_embed,
        name="delete-notion-embed",
    ),
    path(
        "update-notion-embed-name/<int:pk>",
        update_notion_embed_name,
        name="update-notion-embed-name",
    ),
    path(
        "update-notion-embed-database/<int:pk>",
        update_notion_embed_database,
        name="update-notion-embed-database",
    ),
    path("notion-embeds-list", notion_embeds_list_view, name="notion-embeds-list-view"),
    path(
        "update-notion-embed-properties-settings/<int:pk>",
        update_notion_embed_properties_settings,
        name="update-notion-embed-properties-settings",
    ),
]

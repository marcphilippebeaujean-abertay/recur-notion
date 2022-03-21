import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from notion_database.models import NotionPropertyMetaData
from notion_database.service import query_saved_notion_database_model_with_api_update
from security.security_decorator import notion_workspace_authorization_required

from .models import NotionDatabaseEmbed

# Get an instance of a logger
from .service import (
    create_notion_property_settings_from_notion_database_and_embed_model,
)

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
@notion_workspace_authorization_required
@require_http_methods(["GET"])
def notion_embeds_list_view(request):
    return render(
        request,
        "notion-embed/notion-embed-list-view.html",
        {
            "notion_embeds": NotionDatabaseEmbed.objects.filter(creator=request.user),
        },
    )


@login_required
@notion_workspace_authorization_required
@require_http_methods(["POST"])
def create_notion_embed(request):
    created_embed = NotionDatabaseEmbed.objects.create(
        creator=request.user, name="New Notion Database Widget"
    )
    messages.success(request, f"Successfully created a new Notion Widget!")
    return redirect("notion-embed-view", pk=created_embed.pk)


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_notion_embed(request, pk):
    try:
        notion_embed_to_remove_model = NotionDatabaseEmbed.objects.filter(
            pk=pk, creator=request.user
        )[0]
    except IndexError:
        return HttpResponse("Could not find notion embed.", status=404)
    deleted_embed_pk, deleted_embed_name = (
        notion_embed_to_remove_model.pk,
        notion_embed_to_remove_model.name,
    )
    notion_embed_to_remove_model.delete()
    if "X-Hx-Partial" in request.headers and request.headers["X-Hx-Partial"] == "true":
        return HttpResponse(
            f"""
        <div class='alert alert-success mt-2 alert-dismissible fade show'>
            Deleted Notion Embed \"{deleted_embed_name}\"!
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        """,
            status=200,
        )
    messages.success(
        request, f'Successfully Deleted Task with name "{deleted_embed_name}"!'
    )
    return redirect(reverse("notion-embeds-list-view"))


@login_required
@notion_workspace_authorization_required
@require_http_methods(["POST"])
def update_notion_embed_name(request, pk):
    if "embed-name" not in request.POST:
        return HttpResponse("Invalid parameters for updating notion-embed!", status=400)
    try:
        notion_embed = NotionDatabaseEmbed.objects.get(pk=pk, creator=request.user)
        notion_embed.name = request.POST["embed-name"]
        notion_embed.save()
    except NotionDatabaseEmbed.DoesNotExist:
        return HttpResponse("Could not find Task for Update", status=404)
    return HttpResponse(status=200)


@login_required
@notion_workspace_authorization_required
@require_http_methods(["POST"])
def update_notion_embed_database(request, pk):
    if "newDatabaseId" not in request.POST:
        return HttpResponse("Invalid parameters for updating notion-embed!", status=400)
    # fetch database
    database_fetched = query_saved_notion_database_model_with_api_update(
        user_model=request.user, database_id_str=request.POST["newDatabaseId"]
    )
    # set database
    try:
        updated_notion_embed_model = NotionDatabaseEmbed.objects.get(
            creator=request.user, pk=pk
        )
    except NotionDatabaseEmbed.DoesNotExist as e:
        return HttpResponse(status=404)
    updated_notion_embed_model.notion_database = database_fetched
    notion_property_settings = (
        create_notion_property_settings_from_notion_database_and_embed_model(
            notion_embed_model=updated_notion_embed_model,
            notion_database_model=database_fetched,
        )
    )
    updated_notion_embed_model.save()
    return render(
        request,
        "notion-embed/notion-embed-editor.html",
        {
            "notion_embed": updated_notion_embed_model,
            "embed_notion_property_settings": notion_property_settings,
        },
    )


@login_required
@notion_workspace_authorization_required
@require_http_methods(["GET"])
def notion_embed_view(request, pk):
    try:
        notion_embed_model = NotionDatabaseEmbed.objects.filter(
            pk=pk, creator=request.user
        ).prefetch_related("notion_database")[0]
    except IndexError:
        return HttpResponse("Could not find notion embed.", status=404)
    if notion_embed_model.notion_database is None:
        return render(
            "notion-embed/notion-embed-no-active-db-view.html",
            {"notion_embed": notion_embed_model},
        )

    updated_database_model = query_saved_notion_database_model_with_api_update(
        user_model=request.user,
        database_id_str=notion_embed_model.notion_database.notion_id,
    )
    notion_property_settings = (
        create_notion_property_settings_from_notion_database_and_embed_model(
            notion_embed_model=notion_embed_model,
            notion_database_model=updated_database_model,
        )
    )
    return render(
        request,
        "notion-embed/notion-embed-view.html",
        {
            "notion_embed": notion_embed_model,
            "embed_notion_property_settings": notion_property_settings,
        },
    )


@login_required
@require_http_methods(["POST"])
def update_notion_embed_properties_settings(request, pk):
    try:
        embed_property_settings_to_be_updated_list = (
            NotionDatabaseEmbed.objects.filter(pk=pk, creator=request.user)
            .prefetch_related("notion_property_settings")[0]
            .notion_property_settings.all()
        )
    except IndexError:
        return HttpResponse("Could not find notion embed.", status=404)
    for embed_property_settings in embed_property_settings_to_be_updated_list:
        if embed_property_settings.property.notion_id in request.POST.keys():
            embed_property_settings.should_be_visible = True
        else:
            embed_property_settings.should_be_visible = False
        embed_property_settings.save()

    return HttpResponse(status=200)

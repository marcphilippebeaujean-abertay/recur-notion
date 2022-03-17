from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .service import query_user_notion_databases_from_api_as_model_list


# Create your views here.
@login_required
@require_http_methods(["POST"])
def search_workspace_databases_for_notion_embed_db_change(request):
    query_string = request.POST.get("database-search-query", "")
    databases_list = query_user_notion_databases_from_api_as_model_list(
        user_model=request.user, query_string=query_string
    )
    return render(
        request,
        "notion-embed/partials/notion-databases-search-result.html",
        {"databases": databases_list, "embed_pk": request.POST.get("embedPk")},
    )

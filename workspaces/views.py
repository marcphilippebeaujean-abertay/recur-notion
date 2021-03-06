import logging
import urllib.parse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from config.settings import NOTION_CLIENT_ID, NOTION_OAUTH_CALLBACK

from .service import create_access_workspace_from_user_code

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
@require_http_methods(["GET"])
def add_notion_workspace_from_access_code(request):
    logger.info("Fetching Notion workspace from access_code!")
    oauth_request_code_string = request.GET.get("code", None)
    if oauth_request_code_string is None or oauth_request_code_string == "":
        logger.warning("Did not have the request code!")
        return HttpResponseBadRequest(
            "You need to provide an OAuth2 Code to get Access"
        )
    try:
        create_access_workspace_from_user_code(
            user_model=request.user, oauth_code=oauth_request_code_string
        )
    except Exception as e:
        return HttpResponseServerError("Error occurred trying to authorize with Notion")
    return redirect("recurring-tasks-view")


@login_required
def show_notion_access_prompt(request):
    return render(
        request,
        "workspaces/notion-auth.html",
        {
            "client_id": NOTION_CLIENT_ID,
            "callback_url": urllib.parse.quote(NOTION_OAUTH_CALLBACK),
        },
    )

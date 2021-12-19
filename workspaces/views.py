from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render

from config.settings import NOTION_OAUTH_CALLBACK
from .service import create_access_workspace_from_user_code

import logging
from requests.utils import requote_uri

logger = logging.getLogger(__name__)


# Create your views here.
@login_required
@require_http_methods(["GET"])
def add_notion_workspace_from_access_code(request):
    logger.info("Fetching Notion workspace from access_code!")
    oauth_request_code_string = request.GET.get('code', None)
    if oauth_request_code_string is None or oauth_request_code_string == '':
        logger.warning("Did not have the request code!")
        return HttpResponseBadRequest('You need to provide an OAuth2 Code to get Access')
    try:
        create_access_workspace_from_user_code(user_model=request.user, oauth_code=oauth_request_code_string)
    except Exception:
        return HttpResponseServerError("Error occurred trying to authorize with Notion")
    return redirect('recurring-tasks-view')


@login_required
def show_notion_access_prompt(request):
    return render(request, "workspaces/notion-auth.html", {'callback_url': requote_uri(NOTION_OAUTH_CALLBACK)})

from functools import wraps
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url
from django.urls import reverse_lazy

import config.settings as settings
from tasks.models import RecurringTask
from workspaces.models import NotionWorkspaceAccess


def user_passes_test(
    test_func,
    on_failure_redirect_url=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    message="",
):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not test_func(request.user) and len(message) > 0:
                messages.add_message(
                    request, messages.ERROR, message, extra_tags="alert alert-danger"
                )
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(
                on_failure_redirect_url or settings.LOGIN_URL
            )
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


def notion_workspace_authorization_required(view_func=None):
    """
    Decorator for views that require that the user has an active Workspace.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated
        and NotionWorkspaceAccess.objects.filter(owner=u).count() > 0,
        on_failure_redirect_url=reverse_lazy("notion-access-prompt"),
        redirect_field_name="",
        message="",
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def check_free_tasks_usage_limit(view_func=None):
    """
    Decorator for views that require to check for Workspace Tasks limit.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated
        and RecurringTask.objects.filter(owner=u).count()
        < settings.NUM_FREE_RECURRING_TASKS,
        on_failure_redirect_url=reverse_lazy("recurring-tasks-view"),
        redirect_field_name="",
        message=f"You exceeded the limit for the free plan!",
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

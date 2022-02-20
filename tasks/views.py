import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods

from notion_database.thread_processes import FetchUserDatabasesThread
from notion_properties.dto import NotionPropertyDto
from workspaces.models import NotionWorkspaceAccess

from .models import RecurringTask
from .service import (
    RecurringTaskBadFormData,
    RecurringTaskMissingDatabaseException,
    RecurringTaskNotFoundException,
    get_recurring_task_with_properties_update,
    update_recurring_task_interval,
    update_recurring_task_name,
    update_recurring_task_start_time,
    update_task_notion_database,
    update_task_notion_properties_from_request_dict,
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
@login_required
@require_http_methods(["GET"])
def recurring_tasks_view(request):
    notion_workspace_access_grants_queryset = NotionWorkspaceAccess.objects.filter(
        owner=request.user
    )
    if notion_workspace_access_grants_queryset.count() == 0:
        return redirect("notion-access-prompt")
    return render(
        request,
        "tasks/recurring-tasks-list-view.html",
        {"recurring_tasks": request.user.tasks.all()},
    )


@login_required
@require_http_methods(["POST"])
def create_recurring_task(request):
    created_task = RecurringTask.objects.create(
        start_time=now() + datetime.timedelta(days=1), owner=request.user
    )
    return redirect("recurring-task-view", pk=created_task.pk)


@login_required
@require_http_methods(["DELETE"])
def delete_recurring_task(request, pk):
    try:
        task_to_remove_model = RecurringTask.objects.filter(pk=pk, owner=request.user)[
            0
        ]
    except IndexError:
        return HttpResponse("Could not find recurring task.", status=404)
    task_to_remove_model.delete()
    return HttpResponse("", status=200)


@login_required
@require_http_methods(["POST"])
def update_recurring_task_schedule(request, pk):
    try:
        if "interval" in request.POST:
            recurring_task_to_update_model = update_recurring_task_interval(
                user=request.user,
                task_pk=pk,
                interval_value_str=request.POST["interval"],
            )
        elif "task-name" in request.POST:
            recurring_task_to_update_model = update_recurring_task_name(
                user=request.user,
                task_pk=pk,
                new_task_name_str=request.POST["task-name"],
            )
        elif "start-time" in request.POST and "X-Client-Timezone" in request.headers:
            recurring_task_to_update_model = update_recurring_task_start_time(
                user=request.user,
                task_pk=pk,
                start_time_as_string=request.POST["start-time"],
                client_timezone=request.headers["X-Client-Timezone"],
            )
        else:
            return HttpResponse("Invalid parameters for updating tasks!", status=400)
    except RecurringTaskBadFormData:
        return HttpResponse("Invalid parameters for updating tasks!", status=400)
    except RecurringTaskNotFoundException:
        return HttpResponse("Could not find Task for Update", status=404)
    if "update-schedule-only" in request.POST:
        return render(
            request,
            "tasks/partials/recurring-task-schedule.html",
            {
                "recurring_task": recurring_task_to_update_model,
                "show_changed": True,
            },
        )
    return HttpResponse(status=200)


@login_required
@require_http_methods(["POST"])
def update_recurring_task_properties(request, pk):
    try:
        updated_recurring_task_model = update_task_notion_properties_from_request_dict(
            user=request.user, property_value_by_id_dict=request.POST, task_pk=pk
        )
    except RecurringTaskNotFoundException:
        return HttpResponse("Could not find Task for Update", status=404)
    except RecurringTaskBadFormData:
        return HttpResponse("Invalid parameters for updating tasks!", status=400)
    except RecurringTaskMissingDatabaseException:
        return HttpResponse(
            "No Database assigned to task so properties cannot be updated.", status=400
        )
    return render(
        request,
        "tasks/partials/recurring-task-update-property-form.html",
        {"recurring_task": updated_recurring_task_model, "show_changed": True},
    )


@login_required
@require_http_methods(["POST"])
def update_recurring_task_database(request, pk):
    if "X-Selected-Database-Id" not in request.headers:
        return HttpResponse("Invalid parameters for updating tasks!", status=400)
    try:
        updated_recurring_task_model = update_task_notion_database(
            user=request.user,
            database_id=request.headers["X-Selected-Database-Id"],
            task_pk=pk,
        )
    except RecurringTaskNotFoundException:
        return HttpResponse("Could not find Task for Update", status=404)
    return render(
        request,
        "tasks/partials/recurring-task-update-property-form.html",
        {
            "recurring_task": updated_recurring_task_model,
        },
    )


@login_required
def get_recurring_tasks(request):
    return render(
        request,
        "tasks/partials/recurring-tasks-list.html",
        {"recurring_tasks": request.user.tasks.all()},
    )


@login_required
def recurring_task_view(request, pk):
    try:
        recurring_task_model = get_recurring_task_with_properties_update(
            task_pk=pk, owner_user_model=request.user
        )
    except RecurringTaskNotFoundException:
        return render(request, "404.html", status=404)
    return render(
        request,
        "tasks/recurring-task-view.html",
        {"recurring_task": recurring_task_model},
    )

import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods

from workspaces.models import NotionWorkspaceAccess

from .models import RecurringTask
from .service import (
    RecurringTaskBadFormData,
    RecurringTaskNotFoundException,
    update_recurring_task_schedule_from_request_data,
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
        recurring_task_to_update_model = (
            update_recurring_task_schedule_from_request_data(
                request=request, task_pk=pk
            )
        )
    except RecurringTaskNotFoundException:
        return HttpResponse("Could not find Task for Update", status=404)
    except RecurringTaskBadFormData:
        return HttpResponse("Invalid parameters for updating tasks!", status=400)
    if "update-schedule-only" in request.POST:
        return render(
            request,
            "tasks/partials/recurring-task-schedule.html",
            {"recurring_task": recurring_task_to_update_model},
        )
    return HttpResponse(status=200)


@login_required
@require_http_methods(["POST"])
def update_recurring_task_properties(request, pk):
    try:
        updated_recurring_task_model = update_task_notion_properties_from_request_dict(
            request_dict=request, task_pk=pk
        )
    except RecurringTaskNotFoundException:
        return HttpResponse("Could not find Task for Update", status=404)
    except RecurringTaskBadFormData:
        return HttpResponse("Invalid parameters for updating tasks!", status=400)
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
    recurring_task_model = RecurringTask.objects.filter(pk=pk, owner=request.user)[0]
    return render(
        request,
        "tasks/recurring-task-view.html",
        {"recurring_task": recurring_task_model},
    )

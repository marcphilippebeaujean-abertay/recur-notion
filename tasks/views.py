import datetime
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods

from config.settings import NUM_FREE_RECURRING_TASKS
from notion_properties.forms import NotionPropertyForm
from security.security_decorator import (
    check_free_tasks_usage_limit,
    notion_workspace_authorization_required,
)
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
@notion_workspace_authorization_required
@require_http_methods(["GET"])
def recurring_tasks_list_view(request):
    tasks_query = request.user.tasks.all()
    return render(
        request,
        "tasks/recurring-tasks-list-view.html",
        {
            "recurring_tasks": tasks_query,
            "num_remaining_tasks": max(
                NUM_FREE_RECURRING_TASKS - tasks_query.count(), 0
            ),
        },
    )


@login_required
@notion_workspace_authorization_required
@check_free_tasks_usage_limit
@require_http_methods(["POST"])
def create_recurring_task(request):
    created_task = RecurringTask.objects.create(
        start_time=now() + datetime.timedelta(days=1),
        owner=request.user,
        workspace=NotionWorkspaceAccess.objects.filter(owner=request.user)[0].workspace,
    )
    messages.success(request, f"Successfully Created a new Recurring Task!")
    return redirect("recurring-task-view", pk=created_task.pk)


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_recurring_task(request, pk):
    try:
        task_to_remove_model = RecurringTask.objects.filter(pk=pk, owner=request.user)[
            0
        ]
    except IndexError:
        return HttpResponse("Could not find recurring task.", status=404)
    deleted_task_pk, deleted_task_name = (
        task_to_remove_model.pk,
        task_to_remove_model.name,
    )
    task_to_remove_model.delete()
    if "X-Hx-Partial" in request.headers and request.headers["X-Hx-Partial"] == "true":
        return HttpResponse(
            f"""
        <div class='alert alert-success mt-2 alert-dismissible fade show'>
            Deleted task \"{deleted_task_name}\"!
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
        """,
            status=200,
        )
    messages.success(
        request, f'Successfully Deleted Task with name "{deleted_task_name}"!'
    )
    return redirect(reverse("recurring-tasks-view"))


@login_required
@check_free_tasks_usage_limit
@require_http_methods(["POST"])
def duplicate_recurring_task(request, pk):
    try:
        task_to_duplicate = RecurringTask.objects.filter(pk=pk, owner=request.user)[0]
    except IndexError:
        return HttpResponse("Could not find recurring task.", status=404)

    duplicated_task = RecurringTask.objects.create(
        name=task_to_duplicate.name + " Copy",
        owner=request.user,
        database=task_to_duplicate.database,
        interval=task_to_duplicate.interval,
        start_time=task_to_duplicate.start_time,
        properties_json=task_to_duplicate.properties_json,
        workspace=task_to_duplicate.workspace,
    )
    messages.success(
        request, f'Successfully Duplicated Task with Name "{task_to_duplicate.name}"!'
    )
    return redirect(reverse("recurring-task-view", kwargs={"pk": duplicated_task.pk}))


@login_required
@notion_workspace_authorization_required
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
        return HttpResponse(
            f"{recurring_task_to_update_model.days_till_schedule_preview_text}",
            status=200,
        )
    return HttpResponse(status=200)


@login_required
@notion_workspace_authorization_required
@require_http_methods(["POST"])
def update_recurring_task_properties(request, pk):
    try:
        task_to_update = RecurringTask.objects.filter(pk=pk, owner=request.user)[0]
        property_form = NotionPropertyForm(
            request.POST, task_model=task_to_update, show_save_notification=True
        )
        if not property_form.is_valid():
            raise RecurringTaskBadFormData("Form data was not valid!")
        updated_recurring_task_model = update_task_notion_properties_from_request_dict(
            property_value_by_id_dict=property_form.cleaned_data,
            task_model=task_to_update,
        )
    except IndexError:
        return HttpResponse("Could not find Task for Update", status=404)
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
        {
            "recurring_task": updated_recurring_task_model,
            "property_form": property_form,
        },
    )


@login_required
@require_http_methods(["POST"])
def update_recurring_task_database(request, pk):
    if "newDatabaseId" not in request.POST:
        return HttpResponse("Invalid parameters for updating tasks!", status=400)
    try:
        updated_recurring_task_model = update_task_notion_database(
            user=request.user,
            database_id=request.POST["newDatabaseId"],
            task_pk=pk,
        )
    except RecurringTaskNotFoundException:
        return HttpResponse("Could not find Task for Update", status=404)
    property_form = NotionPropertyForm(task_model=updated_recurring_task_model)
    return render(
        request,
        "tasks/partials/recurring-task-update-property-form.html",
        {
            "recurring_task": updated_recurring_task_model,
            "property_form": property_form,
        },
    )


@login_required
@notion_workspace_authorization_required
@require_http_methods(["GET"])
def recurring_task_view(request, pk):
    try:
        recurring_task_model = get_recurring_task_with_properties_update(
            task_pk=pk, owner_user_model=request.user
        )
    except RecurringTaskNotFoundException:
        return render(request, "404.html", status=404)
    property_form = NotionPropertyForm(task_model=recurring_task_model)
    return render(
        request,
        "tasks/recurring-task-view.html",
        {"recurring_task": recurring_task_model, "property_form": property_form},
    )

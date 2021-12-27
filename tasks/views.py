from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from workspaces.models import NotionWorkspaceAccess
from .service import RecurringTaskNotFound, RecurringTaskBadFormData, update_recurring_task_from_request_data,  fetch_notion_workspace_pages_and_convert_to_task_dict
from .models import RecurringTask

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
@login_required
@require_http_methods(["GET"])
def recurring_tasks_view(request):
    notion_workspace_access_grants_queryset = NotionWorkspaceAccess.objects.filter(owner=request.user)
    if notion_workspace_access_grants_queryset.count() is 0:
        return redirect('notion-access-prompt')
    return render(request, "tasks/tasks-view.html")


@login_required
@require_http_methods(["POST"])
def create_recurring_task(request):
    task_created = RecurringTask.objects.create(name=request.POST['name'],
                                                cloned_task_notion_id=request.POST['id'],
                                                cloned_task_url=request.POST['url'],
                                                database_id=request.POST['database-id'].replace('-', ''),
                                                owner=request.user)
    return render(request, 'tasks/partials/recurring-task-create-form.html', {'recurring_task': task_created,
                                                                              'interval_choices': RecurringTask.TaskIntervals.choices})


@login_required
@require_http_methods(["DELETE"])
def delete_recurring_task(request, pk):
    try:
        task_to_remove_model = request.user.tasks.all().filter(pk=pk)[0]
    except IndexError:
        return HttpResponse('Could not find recurring task.', status=404)
    task_to_remove_model.delete()
    return HttpResponse("", status=200)


@login_required()
@require_http_methods(["POST"])
def update_recurring_task(request, pk):
    try:
        recurring_task_to_update_model = update_recurring_task_from_request_data(request_dict=request,
                                                                                 task_pk=pk)
    except RecurringTaskNotFound:
        return HttpResponse('Could not find Task for Update', status=404)
    except RecurringTaskBadFormData:
        return HttpResponse('Invalid parameters for updating tasks!', status=403)
    return render(request, 'tasks/partials/recurring-task.html', {'recurring_task': recurring_task_to_update_model,
                                                                  'interval_choices': RecurringTask.TaskIntervals.choices})


@login_required
def get_notion_workspace_tasks(request):
    logger.info(f'{request.user.username} fetching notion workspace tasks.')
    tasks = fetch_notion_workspace_pages_and_convert_to_task_dict(user_model=request.user,
                                                                  query_string=request.POST['query'])
    return render(request, "tasks/partials/notion-tasks-list.html", {'tasks': tasks,
                                                                     'interval_choices': RecurringTask.TaskIntervals.choices})

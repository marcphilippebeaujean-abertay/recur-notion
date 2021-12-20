from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from workspaces.models import NotionWorkspaceAccess
from .service import fetch_notion_workspace_pages_and_convert_to_task_dict
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
def create_recurring_task(request):
    task_created = RecurringTask.objects.create(name=request.POST['name'],
                                                cloned_task_notion_id=request.POST['id'],
                                                cloned_task_url=request.POST['url'],
                                                database_id=request.POST['database-id'].replace('-', ''),
                                                owner=request.user)
    return get_recurring_tasks_for_notion_task_id(request=request,
                                                  notion_task_id=task_created.cloned_task_notion_id)


@login_required
def delete_recurring_task(request, pk):
    task_to_remove_model = request.user.tasks.all().filter(pk=pk)[0]
    task_to_remove_model.delete()
    return get_recurring_tasks_for_notion_task_id(request=request, user=request.user,
                                                  notion_task_id=task_to_remove_model.cloned_task_notion_id)


@login_required()
def update_recurring_task(request, pk):
    task_to_update_model = request.user.tasks.all().filter(pk=pk)[0]
    if 'interval' in request.POST:
        task_to_update_model.interval = request.POST['interval']
    if 'start-date' in request.POST:
        task_to_update_model.start_date = request.POST['start-date']
    task_to_update_model.save()
    return get_recurring_tasks_for_notion_task_id(request=request,
                                                  notion_task_id=task_to_update_model.cloned_task_notion_id)


def get_recurring_tasks_for_notion_task_id(request, notion_task_id):
    tasks_queryset = request.user.tasks.all().filter(cloned_task_notion_id=notion_task_id)
    return render(request, "tasks/partials/recurring-tasks-list.html", {'recurring_tasks': tasks_queryset,
                                                                        'interval_choices': RecurringTask.TaskIntervals.choices})


@login_required
def get_notion_workspace_tasks(request):
    logger.info(f'{request.user.username} fetching notion workspace tasks.')
    tasks = fetch_notion_workspace_pages_and_convert_to_task_dict(user_model=request.user,
                                                                  query_string=request.POST['query'])
    return render(request, "tasks/partials/notion-tasks-list.html", {'tasks': tasks,
                                                                     'interval_choices': RecurringTask.TaskIntervals.choices})

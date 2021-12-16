from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from workspaces.models import NotionWorkspaceAccess
from .service import fetch_tasks_for_notion_workspace
from .models import RecurringTask


# Create your views here.
@login_required
def recurring_tasks_view(request):
    notion_workspace_access_grants = NotionWorkspaceAccess.objects.filter(owner=request.user)
    if notion_workspace_access_grants.count() is 0:
        return redirect('notion-access-prompt')
    return render(request, "tasks/tasks-view.html")


@login_required
def create_recurring_task(request):
    RecurringTask.objects.create(name=request.POST['name'],
                                 cloned_task_notion_id=request.POST['id'],
                                 cloned_task_url=request.POST['url'],
                                 database_id=request.POST['database-id'].replace('-', ''),
                                 owner=request.user)
    return get_recurring_tasks_for_user(request)


@login_required
def delete_recurring_task(request, pk):
    task_to_remove = request.user.tasks.all().filter(pk=pk)[0]
    task_to_remove.delete()
    return get_recurring_tasks_for_user(request)


@login_required()
def update_recurring_task(request, pk):
    task_to_update = request.user.tasks.all().filter(pk=pk)[0]
    if 'name' in request.POST and 'start-date' in request.POST:
        task_to_update.name = request.POST['name']
        task_to_update.start_date = request.POST['start-date']
        task_to_update.interval = request.POST['interval']
    task_to_update.save()
    return get_recurring_tasks_for_user(request)


@login_required
def get_recurring_tasks_for_user(request):
    tasks = request.user.tasks.all()
    choices = [[choice[0], choice[1]] for choice in RecurringTask.TaskIntervals.choices]
    return render(request, "tasks/partials/recurring-tasks-list.html",
                  {'tasks': tasks, 'choices': choices})


@login_required
def get_notion_workspace_tasks(request):
    tasks = fetch_tasks_for_notion_workspace(request.user, request.POST['query'])
    return render(request, "tasks/partials/notion-tasks-list.html", {'tasks': tasks})

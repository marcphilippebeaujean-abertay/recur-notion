from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from workspaces.models import NotionWorkspaceAccess
from .service import fetch_notion_workspace_pages_and_convert_to_task_dict
from .models import RecurringTask


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
    RecurringTask.objects.create(name=request.POST['name'],
                                 cloned_task_notion_id=request.POST['id'],
                                 cloned_task_url=request.POST['url'],
                                 database_id=request.POST['database-id'].replace('-', ''),
                                 owner=request.user)
    return get_recurring_tasks_for_user(request)


@login_required
def delete_recurring_task(request, pk):
    task_to_remove_model = request.user.tasks.all().filter(pk=pk)[0]
    task_to_remove_model.delete()
    return get_recurring_tasks_for_user(request)


@login_required()
def update_recurring_task(request, pk):
    task_to_update_model = request.user.tasks.all().filter(pk=pk)[0]
    if 'name' in request.POST and 'start-date' in request.POST:
        task_to_update_model.name = request.POST['name']
        task_to_update_model.start_date = request.POST['start-date']
        task_to_update_model.interval = request.POST['interval']
    task_to_update_model.save()
    return get_recurring_tasks_for_user(request)


@login_required
def get_recurring_tasks_for_user(request):
    tasks_queryset = request.user.tasks.all()
    choices_list = [[choice[0], choice[1]] for choice in RecurringTask.TaskIntervals.choices]
    return render(request, "tasks/partials/recurring-tasks-list.html", {'tasks': tasks_queryset,
                                                                        'choices': choices_list})


@login_required
def get_notion_workspace_tasks(request):
    tasks = fetch_notion_workspace_pages_and_convert_to_task_dict(user_model=request.user,
                                                                  query_string=request.POST['query'])
    return render(request, "tasks/partials/notion-tasks-list.html", {'tasks': tasks})

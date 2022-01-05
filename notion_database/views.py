from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .service import query_user_notion_databases_list


# Create your views here.
@login_required
def get_workspace_databases(request):
    query_string = request.POST.get('query_string, ''')
    databases_list = query_user_notion_databases_list(user_model=request.user, query_string=query_string)
    return render(request, 'notion_databases/partials/notion-databases-list.html', {'databases': databases_list})

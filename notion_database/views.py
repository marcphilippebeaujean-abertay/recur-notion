from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .service import query_user_notion_databases_list, query_user_notion_database_by_id


# Create your views here.
@login_required
def get_workspace_databases(request):
    query_string = request.POST.get('query_string, ''')
    databases_list = query_user_notion_databases_list(user_model=request.user, query_string=query_string)
    return render(request, 'notion-databases/partials/notion-databases-list.html', {'databases': databases_list})


@login_required
def get_database_property_inputs(request):
    database_dict = query_user_notion_database_by_id(user_model=request.user,
                                                     database_id_str=request.POST['selected-database-id'])
    return render(request, 'notion-databases/partials/database-property-inputs.html', {'database': database_dict})

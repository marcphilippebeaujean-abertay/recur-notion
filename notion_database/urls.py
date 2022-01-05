from django.urls import path
from .views import get_workspace_databases


urlpatterns = [
    path('get-workspace-databases/', get_workspace_databases, name='get-workspace-databases'),
]
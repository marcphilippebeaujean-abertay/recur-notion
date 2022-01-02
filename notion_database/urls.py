from django.urls import path
from .views import get_workspace_databases, get_database_property_inputs


urlpatterns = [
    path('get-workspace-databases/', get_workspace_databases, name='get-workspace-databases'),
    path('database-property-inputs/', get_database_property_inputs, name='database-property-inputs')
]
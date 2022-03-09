from django.urls import path

from .views import upgrade_request_view

urlpatterns = [
    path("upgrade-request", upgrade_request_view, name="upgrade-request"),
]

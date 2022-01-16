from django.urls import path

from .views import DataPolicy, HomePageView, Imprint

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("data-policy/", DataPolicy.as_view(), name="data-policy"),
    path("imprint/", Imprint.as_view(), name="imprint"),
]

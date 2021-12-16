from django.urls import path

from .views import HomePageView, DataPolicy, Imprint

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', DataPolicy.as_view(), name='datapolicy'),
    path('about/', Imprint.as_view(), name='imprint'),
]

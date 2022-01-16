from django.urls import path

from .views import add_newsletter_member

urlpatterns = [
    path(
        "add-newsletter-member/",
        add_newsletter_member,
        name="add-newsletter-member",
    ),
]

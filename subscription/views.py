from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET"])
def upgrade_request_view(request):
    send_mail(
        "Payment Request",
        f"User with email {request.user.email} wanted to pay!",
        "admin@albert.so",
        ["marcphilippbeaujean@gmail.com"],
        fail_silently=True,
    )
    return HttpResponse(
        """
        <div class="alert alert-warning">
            These features are still in development!
            <a href="https://mixed-yak-26d.notion.site/Public-Roadmap-07126af04916470fbfa243bf8844e44e">
                Suggest what to build first
            </a>
        </div>
        """
    )

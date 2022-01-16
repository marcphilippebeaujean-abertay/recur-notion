from django.http import HttpResponse
from django.shortcuts import render
from honeypot.decorators import check_honeypot
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

from config.settings import MAILCHIMP_SECRET, MAILCHIMP_SERVER_PREFIX


# Create your views here.
@check_honeypot
def add_newsletter_member(request):
    if "email" not in request.POST:
        return HttpResponse(status_code=400)
    submitted_email = request.POST["email"]
    client = MailChimp(mc_api=MAILCHIMP_SECRET)
    try:
        client.lists.members.create(
            "4187275d9e", {"email_address": submitted_email, "status": "subscribed"}
        )
    except MailChimpError:
        return render(
            request,
            "newsletter/partials/mailchimp_form.html",
            {"error": True, "email": submitted_email},
        )
    return render(
        request,
        "newsletter/partials/mailchimp_form.html",
        {"success": True, "email": submitted_email},
    )

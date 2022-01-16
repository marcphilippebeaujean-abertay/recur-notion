from django.shortcuts import render
from honeypot.decorators import check_honeypot
from mailchimp3 import MailChimp

from config.settings import MAILCHIMP_SECRET, MAILCHIMP_SERVER_PREFIX


# Create your views here.
@check_honeypot
def add_newsletter_member(request):
    submitted_email = request.POST["email"]
    try:
        client = MailChimp(mc_api=MAILCHIMP_SECRET)
        response = client.lists.members.create(
            "4187275d9e", {"email_address": submitted_email, "status": "subscribed"}
        )
        return render(
            request,
            "newsletter/partials/mailchimp_form.html",
            {"success": True, "email": submitted_email},
        )
    except Exception as error:
        return render(
            request,
            "newsletter/partials/mailchimp_form.html",
            {"error": True, "email": submitted_email},
        )

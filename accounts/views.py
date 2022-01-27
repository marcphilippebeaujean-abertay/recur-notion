from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .app_settings import EmailVerificationMethod


class SocialAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        user = sociallogin.account.user
        if user.id:
            return
        try:
            existing_user = User.objects.get(email=user.email)
        except ObjectDoesNotExist:
            pass
        else:
            perform_login(
                request, existing_user, app_settings.EmailVerificationMethod.NONE
            )

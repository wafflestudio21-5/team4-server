from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

from django.utils.crypto import get_random_string

from .models import User
import requests
import time

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.nickname = request.POST.get("nickname")

        if user.nickname is None:
            user.nickname = ""

        nickname = user.nickname

        for i in range(10):
            if not User.objects.filter(nickname=nickname).exists():
                break
            nickname = user.nickname+get_random_string(length=12)

        user.nickname = nickname

        user.save()
        return user

class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    profile_url = "https://openidconnect.googleapis.com/v1/userinfo"

    def complete_login(self, request, app, token, response, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={"access_token": token.token, "alt": "json"},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login
    
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

from django.utils.crypto import get_random_string

from .models import User
import requests
import time

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):

        # dic = sociallogin.account.extra_data
        # print(dic)
        # if sociallogin.user is None:
        #     print("yes")
        # else:
        #     print("no")
        
        user = sociallogin.user
        if user.nickname is not "":
            return

        nickname = time.strftime('%Y%m%d_%H%M%S')
        for i in range(10):
            nickname = user.nickname+get_random_string(length=12)
            if not User.objects.filter(nickname=nickname).exists():
                break
        user.nickname = nickname
        user.save()

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
    
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
import requests
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        oauth_data = sociallogin.account.extra_data
        user.nickname = oauth_data.get("name")
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
    
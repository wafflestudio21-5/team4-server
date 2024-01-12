from django.urls import path
from dj_rest_auth.registration import urls

import Watoon.settings as settings

from dj_rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordResetConfirmView,
    PasswordResetView,
)
from dj_rest_auth.registration.views import ResendEmailVerificationView
from dj_rest_auth import urls

from .views import CustomVerifyEmailView, CustomLoginView, CustomLogoutView, CustomRegisterView

urlpatterns = [
    path('password/reset', PasswordResetView.as_view(), name='rest_password_reset'), # TODO: error occured
    path('password/reset/confirm/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='password_reset_confirm'), # TODO: error occured
       
    path('login', CustomLoginView.as_view(), name='rest_login'),
    path('logout', CustomLogoutView.as_view(), name='rest_logout'),
    path('password/change', PasswordChangeView.as_view(), name='rest_password_change'),
    path('', CustomRegisterView.as_view(), name='rest_register'),
    path('verify-email', CustomVerifyEmailView.as_view(), name='rest_verify_email'),
    path('resend-email', ResendEmailVerificationView.as_view(), name="rest_resend_email"),

]

if settings.REST_USE_JWT:
    from rest_framework_simplejwt.views import TokenVerifyView

    from dj_rest_auth.jwt_auth import get_refresh_view

    urlpatterns += [
        path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
        path('token/refresh', get_refresh_view().as_view(), name='token_refresh'),
    ]
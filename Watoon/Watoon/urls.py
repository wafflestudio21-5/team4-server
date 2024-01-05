"""Watoon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from allauth.account.views import (LoginView,
                                   LogoutView,
                                   SignupView, 

                                   ConfirmEmailView,
                                   EmailVerificationSentView,

                                   PasswordChangeView,
                                   )

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),
    
    # auth
    path('accounts/login/', LoginView.as_view(), name="account-login"),
    path('accounts/logout/', LogoutView.as_view(), name='account-logout'),
    path('accounts/signup/', SignupView.as_view(), name='account-signup'),

    path('accounts/emailconfirm/', ConfirmEmailView.as_view(), name="account-email-confirm"),
    path('accounts/emailsend/', EmailVerificationSentView.as_view(), name="account-email-sent"),

    path('accounts/passwordchange/', PasswordChangeView.as_view(), name="account-password-change"),

    path('accounts/', include('allauth.urls')),

    # rest
    path('api-auth/', include('rest_framework.urls')),
]


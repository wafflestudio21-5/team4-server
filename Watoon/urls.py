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
from django.urls import path, include, re_path

from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from user.views import MyTokenObtainPairView


schema_view = get_schema_view(
    openapi.Info(
        title="watoon",
        default_version="v.1",
        description="watoon API 문서",
        terms_of_service="https://www.watoon.com/terms/",
        contact=openapi.Contact(name="test", email="test@test.com"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # webtoon
    path('', include('webtoon.urls')),
    
    # admin
    path('admin/', admin.site.urls),

    # #JWT
    # path('token/',  MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # path('accounts/emailconfirm/', ConfirmEmailView.as_view(), name="account-email-confirm"),
    # path('accounts/emailsend/', EmailVerificationSentView.as_view(), name="account-email-sent"),

    # # path('accounts/passwordchange/', PasswordChangeView.as_view(), name="account-password-change"),
    
    path('accounts/', include('user.urls')),
    path('accounts/', include('dj_rest_auth.urls')),
    path('accounts/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),

    # rest
    path('api-auth/', include('rest_framework.urls')),
    
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),   
]
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated

from dj_rest_auth.registration.views import VerifyEmailView, RegisterView
from dj_rest_auth.views import LoginView, LogoutView

from allauth.account.views import login as allauth_login

import Watoon.settings as settings 
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from .models import User
from .permissions import IsNotAuthenticated, CustomIsAuthenticated

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



class CustomVerifyEmailView(VerifyEmailView):
    def get(self, request, *args, **kwargs):
        # 기존 로직을 호출하여 이메일 인증을 처리합니다.
        response = super().get(request, *args, **kwargs)
        
        # 이메일 인증 성공 여부를 확인하고 적절한 응답을 반환합니다.
        if response.status_code == 200:
            # 이메일 인증 성공
            return Response({"detail": "Email verification successful"})
        else:
            # 이메일 인증 실패
            return Response({"detail": "Email verification failed"})
        
class CustomLogoutView(LogoutView):
    permission_classes = (CustomIsAuthenticated,)

class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        # Check if the user is already authenticated
        if self.request.user.is_authenticated:
            return Response({"detail": "User is already authenticated."}, status=status.HTTP_400_BAD_REQUEST)

        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()
    
class CustomRegisterView(RegisterView):
    permission_classes = (IsNotAuthenticated,)

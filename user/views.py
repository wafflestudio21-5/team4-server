from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError

from dj_rest_auth.registration.views import VerifyEmailView, RegisterView
from dj_rest_auth.views import LoginView, LogoutView, PasswordResetConfirmView

from allauth.account.forms import default_token_generator
from allauth.account.views import login as allauth_login

import Watoon.settings as settings 
from .serializers import UserSerializer, MyTokenObtainPairSerializer, CustomPasswordResetConfirmSerializer
from .models import User
from .permissions import IsNotAuthenticated, CustomIsAuthenticated

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2',
    ),
)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    serializer_class = CustomPasswordResetConfirmSerializer
    permission_classes = (AllowAny,)
    throttle_scope = 'dj_rest_auth'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # Manually handle the logic to save the data
        self.perform_password_reset(serializer.validated_data)

        return Response({'detail': _('Password has been reset with the new password.')})

    def perform_password_reset(self, validated_data):
        # Extract necessary data and perform password reset logic here
        uid = validated_data['uid']
        token = validated_data['token']
        new_password = validated_data['new_password1']

        # Add your logic here to reset the password using the extracted data
        # For example, you can use the UserModel to retrieve the user and update the password
        try:
            user = User._default_manager.get(pk=uid)
        except User.DoesNotExist:
            raise ValidationError({'uid': [_('Invalid value')]})

        if not default_token_generator.check_token(user, token):
            raise ValidationError({'token': [_('Invalid value')]})

        # Your password reset logic here, for example:
        user.set_password(new_password)
        user.save()


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

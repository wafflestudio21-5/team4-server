from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from allauth.account.views import login as allauth_login

from Watoon.settings import SECRET_KEY
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from .models import User


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.response import Response

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
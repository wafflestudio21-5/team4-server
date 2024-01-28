from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from dj_rest_auth.registration.views import VerifyEmailView, RegisterView, SocialLoginView
from dj_rest_auth.views import LoginView, LogoutView, PasswordResetConfirmView

from allauth.account.forms import default_token_generator
from allauth.account.views import login as allauth_login
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount

import Watoon.settings as settings 
from .serializers import UserSerializer, MyTokenObtainPairSerializer, CustomPasswordResetConfirmSerializer
from .models import User
from .permissions import IsNotAuthenticated, CustomIsAuthenticated
from .adapter import CustomGoogleOAuth2Adapter

from json.decoder import JSONDecodeError
from django.http import JsonResponse
import requests

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

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, uid, token, *args, **kwargs):
        context = {'uid': uid, 'token': token}
        serializer = CustomPasswordResetConfirmSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': _('Password has been reset with the new password.')},
        )

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



BASE_URL = 'http://watoon-env1.eba-ytauqqvt.ap-northeast-2.elasticbeanstalk.com/'
KAKAO_CALLBACK_URI = BASE_URL + 'accounts/kakao/callback/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/callback/'

def kakao_login(request):
    kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
    client_id = settings.SOCIAL_AUTH_KAKAO_REST_API_KEY
    return redirect(f"{kakao_api}&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}")

def kakao_callback(request):
    auth_code = request.GET['code']
    kakao_token_api = 'https://kauth.kakao.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.SOCIAL_AUTH_KAKAO_REST_API_KEY,
        'redirection_uri': KAKAO_CALLBACK_URI,
        'code': auth_code,
    }

    token_req = requests.post(kakao_token_api, data=data)
    token_req_json = token_req.json()

    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get("access_token")

    user_info_req = requests.get('https://kapi.kakao.com/v2/user/me', headers={'Authorization': f'Bearer {access_token}'})
    user_info_req_status = user_info_req.status_code
    
    if user_info_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get user info'}, status=status.HTTP_400_BAD_REQUEST)
    
    user_info_req_json = user_info_req.json()
    kakao_account = user_info_req_json.get('kakao_account')
    email = kakao_account.get('email')
    #nickname = kakao_account.get('profile').get('nickname')
    #print(email, nickname)
    try:
        user = User.objects.get(email=email)

        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        data = {'access_token': access_token, 'code': auth_code}
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        data = {'access_token': access_token, 'code': auth_code}
        
        accept = requests.post(f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except SocialAccount.DoesNotExist:
        return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)

class KakaoLogin(SocialLoginView):
    permission_classes = (IsNotAuthenticated,)
    adapter_class = KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client

def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    client_id = settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID
    client_secret = settings.SOCIAL_AUTH_GOOGLE_CLIENT_SECRET
    state = settings.STATE
    code = request.GET['code']

    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)
    
    access_token = token_req_json.get("access_token")

    email_req = requests.post(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    email_req_json = email_req.json()
    email = email_req_json.get("email")
    
    #회원가입/로그인
    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)

        # 있는데 구글계정이 아니어도 에러
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 우저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:    # DoesNotExist -> Django Model에서 기본 지원
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}

        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except SocialAccount.DoesNotExist:
    	# User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
        return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)

class GoogleLogin(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


def NickNameVerify(request, nickname):
    user = User.objects.get(nickname=nickname)
    if user is None:
        return JsonResponse({"nickname" : "possible"})
    return JsonResponse({"nickname": "impossible"})
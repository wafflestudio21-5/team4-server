# from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, PasswordResetConfirmSerializer

from allauth.account.adapter import get_adapter
from allauth.account.utils import url_str_to_user_pk as uid_decoder

from .models import User
import Watoon.settings as settings


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email

        return token

class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=settings.ACCOUNT_EMAIL_REQUIRED)
    password = serializers.CharField(write_only=True)

class CustomRegisterSerializer(RegisterSerializer):
    username = None
    nickname = serializers.CharField(required=True, max_length=15, min_length=1)
    email = serializers.EmailField(required=settings.ACCOUNT_EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
    def save(self, request):
        user = super().save(request)
        user.nickname = self.data.get('nickname')
        user.save()
        return user
        
    def validate_nickname(self, nickname):
        # Check for special characters in the nickname
        if not nickname.isalnum():
            raise serializers.ValidationError(
                _('Nickname should only contain alphanumeric characters.')
            )

        # Check if the nickname is already in use
        if User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError(
                _('A user with this nickname already exists.')
            )

        return nickname
    
    
class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    def __init__(self, *args, **kwargs):
        # URL 매개변수를 가져와서 기본값 설정
        uid_param = kwargs['context']['request'].parser_context['kwargs'].get('uid', None)
        token_param = kwargs['context']['request'].parser_context['kwargs'].get('token', None)

        data = {'uid': uid_param, 'token': token_param}
        data.update(kwargs.get('data', {}))
        
        kwargs['data'] = data

        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
            from allauth.account.utils import url_str_to_user_pk as uid_decoder
        else:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_decode as uid_decoder

        # Decode the uidb64 (allauth use base36) to uid to get User object
        try:
            uid = force_str(uid_decoder(attrs['uid']))
            self.user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'uid': [_('Invalid value')]})

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': [_('Invalid value')]})

        self.custom_validation(attrs)  # 사용자 정의 유효성 검사

        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs,
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)

        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only':True},
        }
    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            nickname = validated_data['nickname'],
            password = validated_data['password'],
        )
        return user



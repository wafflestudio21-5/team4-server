# from django.conf import settings
from django.utils.translation import gettext_lazy as _

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
        # Get the request from the context
        self.request = kwargs.pop('context', {}).get('request')
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        # If request is available, try to get uid and token from the URL
        if self.request:
            uidb64 = self.request.parser_context['kwargs'].get('uidb64')
            token = self.request.parser_context['kwargs'].get('token')

            # Set default values for uid and token if not provided in the URL
            attrs.setdefault('uid', uidb64)
            attrs.setdefault('token', token)

            if uidb64:
                attrs['uid'] = uid_decoder(uidb64)
            if token:
                attrs['token'] = token

        # Call the parent validate method
        return super().validate(attrs)

    def custom_validation(self, attrs):
        # Your custom validation logic goes here
        pass

    def save(self):
        # Your save logic goes here
        return super().save()

    class Meta:
        model = User

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
            password = validated_data['password']
        )
        return user



# from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer

from allauth.account.adapter import get_adapter

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



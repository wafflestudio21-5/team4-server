from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import validate_no_special_characters

class User(AbstractUser):
    email = models.EmailField(unique=True) # 로그인 시 아이디로 사용
    nickname = models.CharField(
        max_length=15,
        unique=True,
        error_messages={
            "unique": "이미 사용 중인 닉네임입니다."
        },
        validators=[validate_no_special_characters]
        )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.nickname

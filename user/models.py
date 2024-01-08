from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True) # 로그인 시 아이디로 사용
    nickname = models.CharField(max_length=15)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username
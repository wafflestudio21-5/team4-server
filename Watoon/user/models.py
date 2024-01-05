from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from .validators import validate_no_special_characters, validate_password


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, nickname, password):
        if not email:
            raise ValueError('The Email field must be set')
        
        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname
        )
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password):
        user = self.create_user(            
            email = self.normalize_email(email),            
            nickname = nickname,            
            password = password        
        )        
        user.is_admin = True        
        user.is_superuser = True        
        user.is_staff = True

        user.save(using=self._db)        
        return user

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    
    email = models.EmailField(max_length=255, unique=True) # 로그인 시 아이디로 사용
    nickname = models.CharField(
        max_length=15,
        null=False,
        unique=True,
        error_messages={
            "unique": "이미 사용 중인 닉네임입니다."
        },
        validators=[validate_no_special_characters]
        )
    password = models.CharField(max_length=128, validators=[validate_password])
         
    is_active = models.BooleanField(default=True) 
    is_superuser = models.BooleanField(default=False)    
    is_staff = models.BooleanField(default=False)   

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def __str__(self):
        return self.nickname

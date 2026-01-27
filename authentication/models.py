from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0) 
    is_blocked = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"{self.user.email} - {self.code}"

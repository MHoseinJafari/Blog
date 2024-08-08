from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core import exceptions
from rest_framework.exceptions import ParseError



class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_query_name='profile', related_name='profile')
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ('-id',)
    
    def __str__(self) -> str:
        return '{}-{}'.format(self.user.username, self.email)
    
    @property
    def fullname(self) -> str:
        return '{} {}'.format(self.first_name, self.last_name)
    
    @property
    def username(self) -> str:
        return self.user.username
    
    @staticmethod
    def create_profile(user) -> 'Profile':
        Profile.objects.create(user=user)

    @staticmethod
    def password_validater(password:str, new_pass:str) -> str:
        if password != new_pass:
            raise serializers.ValidationError(
                {"detail": "passwords doesnt match"}
            )
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"passwords errors": list(e.messages)}
            )

    @staticmethod
    def check_pass(password: str, object) -> str:
        if not object.check_password(password):
            raise ParseError("wrong current password")
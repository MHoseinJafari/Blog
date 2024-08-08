from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import NotAcceptable

from .models import Profile




class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50, write_only=True)
    new_pass = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = Profile
        fields = ['username', 'password', 'new_pass']
    
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        password = data.get('password')
        new_pass = data.get('new_pass')
        username = data.get('username')
        Profile.password_validater(password, new_pass)
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already exists."})
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        username = data.get('username')
        password = data.get('password')
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotAcceptable({"detail": "invalid username"})
        Profile.check_pass(password, user_obj)
        return data


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ["id", "email", "first_name", "last_name"]
        read_only_fields = ['email'] 
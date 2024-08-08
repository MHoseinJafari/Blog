from . import serializers
from .models import Profile
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction


class Signup(APIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = User.objects.create_user(
                username=username, password=password
            )
            Profile.create_profile(user=user)
            token = RefreshToken.for_user(user)
            data = {
                "refresh": str(token),
                "access": str(token.access_token),
            }
            response = {"detail": "succeed", "tokens": data}
            return Response(data=response, status=status.HTTP_201_CREATED)


class Login(APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        user = User.objects.get(username=username)
        token = RefreshToken.for_user(user)
        data = {
            "refresh": str(token),
            "access": str(token.access_token),
        }
        response = {"detail": "succeed", "tokens": data}
        return Response(data=response)


class ProfileApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

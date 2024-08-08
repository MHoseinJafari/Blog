from .models import Post
from . import serializers
from django.db import transaction

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response


from user.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class PostModelViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(visible=True)
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    OrderingFilter = ["created_date"]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.PostCreateSerializer
        return serializers.PostSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            user = self.request.user
            instance = serializer.save(author=user)
            return instance


class VoteApiView(APIView):
    serializer_class = serializers.VoteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data["vote"]
        post = serializer.validated_data["post"]
        post.vote_submit(user=request.user, amount=vote)
        return Response(
            {"detail": "Your vote has been successfully submitted"}
        )

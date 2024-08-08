from .models import Post, Vote
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import NotAcceptable
from .messages import Message





class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['vote', 'post', 'created_date']


    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        post = data['post']

        if post.visible == False:
            raise NotAcceptable(Message.invalid_post)
        return data


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content']


class PostSerializer(serializers.ModelSerializer):
    vote = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'voters', 'rate', 'created_date', 'vote']
        read_only_fields = ['author', 'rate', 'voters', ]
    
    def get_vote(self, obj):
        vote = Vote.objects.filter(post = obj, user=self.context['request'].user.id).first()
        serializer = VoteSerializer(instance=vote)
        return serializer.data
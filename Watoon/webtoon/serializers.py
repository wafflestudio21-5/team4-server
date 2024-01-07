
from rest_framework import serializers
from .models import UserProfile, Webtoon, Episode, Comment, Tag


class TagSerializer(serializers.ModelSerializer):
    """태그 Serializer"""
    class Meta:
        model = Tag
        field = ['content']


class WebtoonInfoSerializer(serializers.ModelSerializer):
    """Webtoon 리스트에서 보여지는 Webtoon의 Serializer"""
    class Meta:
        model = Webtoon
        fields = ['id', 'title', 'titleImage']


class WebtoonContentSerializer(serializers.ModelSerializer):
    """Webtoon 페이지 안에서의 Serializer"""
    totalRating = serializers.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    tags = TagSerializer(many=True)
    class Meta:
        model = Webtoon
        fields = ['id', 'title', 'titleImage', 'description', 'uploadDays', 'author', 'totalRating', 'tags']


class EpisodeInfoSerializer(serializers.ModelSerializer):
    """Webtoon 페이지에서 보여지는 Episode의 Serializer"""
    class Meta:
        model = Episode
        fields = ['id', 'title', 'episodeNumber', 'thumbnail', 'rating', 'releasedDate']


class EpisodeContentSerializer(serializers.ModelSerializer):
    """Episode 페이지 안에서의 Serializer"""
    class Meta:
        model = Episode
        fields = ['id', 'title', 'content', 'rating']


class SubCommentSerializer(serializers.ModelSerializer):
    """대댓글을 보여주기 위한 Nested Serializer 용도로 사용"""
    likedNumber = serializers.IntegerField(default=0)
    dislikedNumber = serializers.IntegerField(default=0)
    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy', 'likedNumber', 'dislikedNumber']


class CommentSerializer(serializers.ModelSerializer):
    """댓글 Serializer"""
    comments = SubCommentSerializer(many=True)
    likedNumber = serializers.IntegerField()
    dislikedNumber = serializers.IntegerField()
    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy', 'comments', 'likedNumber', 'dislikedNumber']


class SubscriberUserProfileSerializer(serializers.ModelSerializer):
    """Subscriber를 보여주기 위한 Nested Serializer 용도로 사용"""
    class Meta:
        model = UserProfile
        field = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """유저 Serializer"""
    webtoons = WebtoonInfoSerializer(many=True)
    subscribingWebtoons = WebtoonInfoSerializer(many=True)
    subscribers = SubscriberUserProfileSerializer(many=True)
    class Meta:
        model = UserProfile
        field = ['id', 'isAuther', 'webtoons', 'subscribingWebtoons', 'subscribers']


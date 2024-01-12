
from rest_framework import serializers
from .models import UserProfile, DayOfWeek, Webtoon, Episode, Comment, Tag
from user.serializers import UserSerializer



class TagSerializer(serializers.ModelSerializer):
    """태그 Serializer"""
    class Meta:
        model = Tag
        fields = ['content']
        extra_kwargs = {
            'content' : {'validators': []},
        }


class DayOfWeekSerializer(serializers.ModelSerializer):
    """요일 Serializer"""
    class Meta:
        model = DayOfWeek
        fields = ["name"]
        extra_kwargs = {
            'name' : {'validators': []},
        }


class WebtoonInfoSerializer(serializers.ModelSerializer):
    """Webtoon 리스트에서 보여지는 Webtoon의 Serializer"""
    author = UserSerializer(read_only = True)
    class Meta:
        model = Webtoon
        #fields = ['id', 'title', 'titleImage', 'releasedDate']
        fields = ['id', 'title', 'releasedDate', 'author']
        read_only_fields = ['releasedDate', 'author']


class WebtoonContentSerializer(serializers.ModelSerializer):
    """Webtoon 페이지 안에서의 Serializer"""
    #totalRating = serializers.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    uploadDays = DayOfWeekSerializer(many=True)
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only = True)
    class Meta:
        model = Webtoon
        fields = ['id', 'title', 'description', 'uploadDays', 'author', 'tags']
        read_only_fields = ['author', 'releasedDate']

        #fields = ['id', 'title', 'titleImage', 'description', 'uploadDays', 'author', 'totalRating', 'tags']
    
    def create(self, validated_data):
            tags = validated_data.pop('tags')
            uploadDays = validated_data.pop('uploadDays')
            webtoon = Webtoon.objects.create(**validated_data)
            
            for tag_data in tags: 
                try :
                    tag = Tag.objects.get(content=tag_data['content'])
                except : 
                    tag = Tag.objects.create(content=tag_data['content'])
                    tag.save()
                tag.webtoons.add(webtoon)
            
            for day_data in uploadDays: 
                try :
                    uploadDay = DayOfWeek.objects.get(name=day_data['name'])
                except : 
                    uploadDay = DayOfWeek.objects.create(name=day_data['name'])
                    uploadDay.save()
                webtoon.uploadDays.add(uploadDay)
                
            return webtoon


class EpisodeInfoSerializer(serializers.ModelSerializer):
    """Webtoon 페이지에서 보여지는 Episode의 Serializer"""
    class Meta:
        model = Episode
        #fields = ['id', 'title', 'episodeNumber', 'thumbnail', 'rating', 'releasedDate']
        fields = ['id', 'title', 'episodeNumber', 'rating', 'releasedDate']
        read_only_fields = ['rating', 'releasedDate']

class EpisodeContentSerializer(serializers.ModelSerializer):
    """Episode 페이지 안에서의 Serializer"""
    webtoon = WebtoonInfoSerializer(read_only=True)

    class Meta:
        model = Episode
        fields = ['id', 'title', 'episodeNumber', 'rating', 'releasedDate', 'webtoon']
        #fields = ['id', 'title', 'episodeNumber', 'thumbnail', 'content', 'rating', 'releasedDate']
        read_only_fields = ['rating', 'releasedDate']

    
class UserProfileInfoSerializer(serializers.ModelSerializer):
    """다른 페이지에서 보이는 유저 Serializer"""
    class Meta:
        model = UserProfile
        fields = ['id']


class SubscriberUserProfileSerializer(serializers.ModelSerializer):
    """Subscriber를 보여주기 위한 Nested Serializer 용도로 사용"""
    class Meta:
        model = UserProfile
        fields = ['id']

class UserProfileContentSerializer(serializers.ModelSerializer):
    """유저 Serializer"""
    webtoons = WebtoonInfoSerializer(many=True)
    subscribingWebtoons = WebtoonInfoSerializer(many=True)
    subscribers = SubscriberUserProfileSerializer(many=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'isAuther', 'webtoons', 'subscribingWebtoons', 'subscribers']


class CommentInfoSerializer(serializers.ModelSerializer):
    """대댓글을 보여주기 위한 Nested Serializer 용도로 사용"""
    #likedNumber = serializers.IntegerField()
    #dislikedNumber = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy',]# 'likedNumber', 'dislikedNumber']
        read_only_fields = ['dtCreated', 'dtUpdated', 'createdBy',]# 'likedNumber', 'dislikedNumber']


class CommentContentSerializer(serializers.ModelSerializer):
    """댓글 Serializer"""
    comments = CommentInfoSerializer(many=True, read_only = True)
    likedBy = UserProfileInfoSerializer(many=True)
    dislikedBy = UserProfileInfoSerializer(many=True)
    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy', 'comments', 'likedBy', 'dislikedBy']
        read_only_fields = ['dtCreated', 'dtUpdated', 'createdBy', 'comments']

    def create(self, validated_data):
        instance = Comment()
        for key in validated_data:
            if key in ['comments', 'likedBy', 'dislikedBy']:
                continue
            setattr(instance, key, validated_data[key])
        instance.save()
        likedBy = validated_data.get('likedBy', instance.likedBy)
        if hasattr(likedBy, '__iter__'):
            for user in instance.likedBy.all():
                instance.likedBy.remove(user)
            for user in likedBy:
                instance.likedBy.add(UserProfile.objects.get(name=user.name))

        dislikedBy = validated_data.get('dislikedBy', instance.dislikedBy)
        if hasattr(dislikedBy, '__iter__'):
            for user in instance.dislikedBy.all():
                instance.dislikedBy.remove(user)
            for user in dislikedBy:
                instance.dislikedBy.add(UserProfile.objects.get(name=user.name))  
        instance.save()
        return instance
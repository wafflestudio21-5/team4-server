from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.validators import MaxLengthValidator, MinLengthValidator, MinValueValidator

from user.models import User
from rest_framework import serializers

from .models import DayOfWeek, Webtoon, Episode, Comment, Tag, Rating, Like, UserProfile, EpisodeImage
from user.serializers import UserSerializer

from rest_framework.exceptions import ValidationError
from Watoon import settings
import boto3



# ///////////////////////////////////////////////////////////////////////////////
# Serializer 작업 때 Image 관련 요소 모두 제거 추후 수정 필요
# ///////////////////////////////////////////////////////////////////////////////




class TagSerializer(serializers.ModelSerializer):
    """태그 Serializer"""
    class Meta:
        model = Tag
        fields = ['content']
        extra_kwargs = {
            'content': {'validators': [MaxLengthValidator(20), MinLengthValidator(1)]}
        }


class RatingSerializer(serializers.ModelSerializer):
    """평점 Serializer"""
    class Meta:
        model = Rating
        fields = ['rating', 'createdBy']
        read_only_fields = ['createdBy']


class LikeSerializer(serializers.ModelSerializer):
    """좋아요/싫어요 Serializer"""
    class Meta:
        model = Like
        fields = ['isLike', 'isDislike', 'createdBy']
        read_only_fields = ['createdBy']
    
    def validate(self, data):
        isLike = data['isLike']
        isDislike = data['isDislike']
        if (isLike and isDislike) or (not isLike and not isDislike):
            raise ValidationError('Like (exclusive) or Dislike should be selected')
        return data
        

class DayOfWeekSerializer(serializers.ModelSerializer):
    """요일 Serializer"""
    class Meta:
        model = DayOfWeek
        fields = ['name']
        extra_kwargs = {
            'name': {'validators': []}
        }


class WebtoonInfoSerializer(serializers.ModelSerializer):
    """Webtoon 리스트에서 보여지는 Webtoon의 Serializer"""
    author = UserSerializer(read_only = True)
    subscribing = serializers.SerializerMethodField(method_name='isSubscribing', read_only=True)
    class Meta:
        model = Webtoon
        fields = ['id', 'title', 'releasedDate', 'author', 'totalRating', 'subscribing', 'titleImage']
        read_only_fields = ['releasedDate', 'author', 'totalRating', 'subscribing']

    def isSubscribing(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.subscribers.filter(pk=user.pk).exists()



class WebtoonContentSerializer(serializers.ModelSerializer):
    """Webtoon 페이지 안에서의 Serializer"""
    uploadDays = DayOfWeekSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer(read_only = True)
    subscribing = serializers.SerializerMethodField(method_name='isSubscribing', read_only=True)
    subscribeCount = serializers.SerializerMethodField(method_name='getSubscribeCount', read_only=True)
    episodeCount = serializers.SerializerMethodField(method_name='getEpisodeCount', read_only=True)
    class Meta:
        model = Webtoon
        fields = ['id', 'title', 'description', 'uploadDays', 'author', 'totalRating', 'episodeCount', 'isFinished', 'tags', 'subscribing', 'subscribeCount',  'titleImage']
        #fields = ['id', 'title', 'titleImage', 'description', 'uploadDays', 'author', 'totalRating', 'tags']
        read_only_fields = ['author', 'releasedDate', 'subscribing', 'subscribeCount', 'totalRating', 'episodeCount']
       
    def create(self, validated_data):
        tags = validated_data.pop('tags') if 'tags' in validated_data else []
        uploadDays = validated_data.pop('uploadDays') if 'uploadDays' in validated_data else []

        # uploadDay 유효성 체크
        uploadDayObjects = []
        for day_data in uploadDays:
            uploadDay = get_object_or_404(DayOfWeek, name=day_data['name'])
            uploadDayObjects.append(uploadDay)

        webtoon = Webtoon.objects.create(**validated_data)

        for tag_data in tags:
            tag, created = Tag.objects.get_or_create(content=tag_data['content'])
            tag.webtoons.add(webtoon)

        for uploadDay in uploadDayObjects:
            webtoon.uploadDays.add(uploadDay)
        
        # if "titleImage" in validated_data:
        #     webtoon.titleImage = validated_data["titleImage"]
        
        return webtoon

    def update(self, instance, validated_data):
        # uploadDays, tags를 제외한 필드는 그냥 값 바꾸기
        for key in validated_data:
            if key in ['uploadDays', 'tags']:
                continue
            setattr(instance, key, validated_data[key])
        print(validated_data)

        # uploadDays 수정
        uploadDays = validated_data.get('uploadDays', instance.uploadDays)
        if hasattr(uploadDays, '__iter__'):
            for uploadDay in instance.uploadDays.all():
                instance.uploadDays.remove(uploadDay)
            for uploadDay in uploadDays:
                instance.uploadDays.add(DayOfWeek.objects.get(name=uploadDay['name']))

        # tags 수정
        tags = validated_data.get('tags')
        if tags is not None:
            for tag in instance.tags.all():
                instance.tags.remove(tag)
            for tag in tags:
                tag_object, created = Tag.objects.get_or_create(content=tag.get('content'))
                instance.tags.add(tag_object)
        instance.save()
        return instance

    def isSubscribing(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.subscribers.filter(pk=user.pk).exists()

    def getSubscribeCount(self, obj):
        return obj.subscribers.count()

    def getEpisodeCount(self, obj):
        return obj.episodes.count()


class EpisodeInfoSerializer(serializers.ModelSerializer):
    """Webtoon 페이지에서 보여지는 Episode의 Serializer"""
    class Meta:
        model = Episode
        fields = ['id', 'title', 'episodeNumber', 'totalRating', 'releasedDate']
        read_only_fields = ['totalRating', 'releasedDate']

class EpisodeImage(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = EpisodeImage
        fields = ['image']


class EpisodeContentSerializer(serializers.ModelSerializer):
    """Episode 페이지 안에서의 Serializer"""
    webtoon = WebtoonInfoSerializer(read_only=True)

    previousEpisode = serializers.SerializerMethodField(method_name='getPreviousEpisode', read_only=True)
    nextEpisode = serializers.SerializerMethodField(method_name='getNextEpisode', read_only=True)
    liking = serializers.SerializerMethodField(method_name='isLiking', read_only=True)
    imageDomain = serializers.SerializerMethodField(method_name='getImageDomain', read_only=True)
    imageUrls = serializers.SerializerMethodField(method_name='getImageUrl',read_only=True)

    images = serializers.SerializerMethodField(method_name='getEpisodeImages', read_only=True)
    class Meta:
        model = Episode
        fields = ['id', 'title', 'episodeNumber', 'totalRating', 'releasedDate', 'webtoon', 'previousEpisode', 'nextEpisode', 'liking', 'likedBy',
                 'imageUrls', 'imageDomain', 'imageNumber', 'images']
        
        read_only_fields = ['totalRating', 'releasedDate', 'previousEpisode', 'nextEpisode', 'liking', 'likedBy', 'imageNumber']
        extra_kwargs = {
            'episodeNumber': {'validators': [MinValueValidator(1)]}
        }

    def create(self, validated_data):
        instance = Episode.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('images'):
            EpisodeImage.objects.create(episode=instance, image=image_data)
        return instance
    
    def update(self, instance, validated_data):
        for key in validated_data:
            if key in ['webtoon']:
                continue
            setattr(instance, key, validated_data[key])
        webtoon = validated_data.get('webtoon', instance.webtoon)
        if not isinstance(webtoon, Webtoon):
            instance.webtoon = Webtoon.objects.get(title=webtoon['title'])
        instance.save()
        return instance

    def getPreviousEpisode(self, obj):
        n = obj.episodeNumber
        webtoon = obj.webtoon
        nextEpisode = Episode.objects.filter(episodeNumber=n-1, webtoon=webtoon)
        if nextEpisode.exists():
            return nextEpisode[0].id
        return None

    def getNextEpisode(self, obj):
        n = obj.episodeNumber
        webtoon = obj.webtoon
        nextEpisode = Episode.objects.filter(episodeNumber=n+1, webtoon=webtoon)
        if nextEpisode.exists():
            return nextEpisode[0].id
        return None
    

    def isLiking(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Like.objects.filter(createdBy=user).filter(episode=obj).exists()

    def getImageDomain(self, obj):
        return settings.S3_URL #+ "/" + str(obj.webtoon.id) + "/" + str(obj.episodeNumber)

    def getImageUrl(self, obj):
        s3 = boto3.client('s3', aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION)
        
        obj_list = s3.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=str(obj.webtoon.id) + "/" + str(obj.episodeNumber) + "/")
        contents_list =  obj_list['Contents']
        file_list = []
        for content in contents_list : 
            key = content['Key']
            file_list.append(key)
        
        return file_list

    def getEpisodeImages(self, obj):
        images = obj.images.all() 
        return EpisodeImageSerializer(instance=images, many=True, context=self.context).data



class SubscriberUserSerializer(serializers.ModelSerializer):
    """Subscriber를 보여주기 위한 Nested Serializer 용도로 사용"""
    class Meta:
        model = User
        fields = ['id', 'nickname']


class UserInfoSerializer(serializers.ModelSerializer):
    """다른 페이지에서 보이는 유저 Serializer"""
    class Meta:
        model = User
        fields = ['id', 'nickname']
    
    def run_validation(self, data):
        value = User.objects.get(nickname=data['nickname'])
        return value


class UserProfileContentSerializer(serializers.ModelSerializer):
    """프로필 페이지 Serializer"""
    id = serializers.SerializerMethodField(method_name='getUserId', read_only=True)
    nickname = serializers.SerializerMethodField(method_name='getNickname', read_only=True)
    subscriberNumber = serializers.SerializerMethodField(method_name='getSubscriberNumber', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'nickname', 'introduction', 'isAuthor', 'subscriberNumber']
        read_only_fields = ['id', 'nickname', 'subscriberNumber']

    def getUserId(self, obj):
        return obj.user.id

    def getNickname(self, obj):
        return obj.user.nickname

    def getSubscriberNumber(self, obj):
        return obj.subscribers.count()


class CommentContentSerializer(serializers.ModelSerializer):
    """댓글 페이지 안에서의 Serializer"""
    # comments = CommentInfoSerializer(many=True, read_only=True)
    subComments = serializers.SerializerMethodField(method_name='getComments', read_only=True)
    createdBy = UserInfoSerializer(read_only=True)
    liking = serializers.SerializerMethodField(method_name='isLiking', read_only=True)
    disliking = serializers.SerializerMethodField(method_name='isDisliking', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy', 'subComments', 'likedBy', 'dislikedBy', 'liking', 'disliking']
        read_only_fields = ['dtCreated', 'dtUpdated', 'createdBy', 'subComments', 'likedBy', 'dislikedBy']

    def getComments(self, obj):
        return obj.comments.count()
    
    def isLiking(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Like.objects.filter(createdBy=user).filter(comment=obj).filter(isLike=True).exists()

    def isDisliking(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Like.objects.filter(createdBy=user).filter(comment=obj).filter(isDislike=True).exists()

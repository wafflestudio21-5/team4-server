from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.validators import MaxLengthValidator, MinLengthValidator

from user.models import User
from rest_framework import serializers

from .models import DayOfWeek, Webtoon, Episode, Comment, Tag, Rating, Like, UserProfile
from user.serializers import UserSerializer

from rest_framework.exceptions import ValidationError
from Watoon import settings



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

    # def run_validation(self, data):
    #     try:
    #         value = Tag.objects.get(pk=data['content'])
    #     except:
    #         value = Tag.objects.create(pk=data['content'])
    #     return value


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
    uploadDays = DayOfWeekSerializer(many=True)
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
        tags = validated_data.pop('tags')
        uploadDays = validated_data.pop('uploadDays')

        # uploadDay 유효성 체크
        uploadDayObjects = []
        for day_data in uploadDays:
            uploadDay = get_object_or_404(DayOfWeek, name=day_data['name'])
            uploadDayObjects.append(uploadDay)

        webtoon = Webtoon.objects.create(**validated_data)

        for tag_data in tags:
            tag, created = Tag.objects.get_or_create(content=tag_data['content'])
            tag.webtoons.add(webtoon)
        # for tag in tags:
        #     tag.webtoons.add(webtoon)

        for uploadDay in uploadDayObjects:
            webtoon.uploadDays.add(uploadDay)
        # for tag in tags:
        #     tag.webtoons.add(webtoon)
        # for day in uploadDays:
        #     day.webtoons.add(webtoon)
        
        if "titleImage" in validated_data:
            webtoon.titleImage = validated_data["titleImage"]
        
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
        instance.update_rating()
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


class EpisodeContentSerializer(serializers.ModelSerializer):
    """Episode 페이지 안에서의 Serializer"""
    webtoon = WebtoonInfoSerializer(read_only=True)

    previousEpisode = serializers.SerializerMethodField(method_name='getPreviousEpisode', read_only=True)
    nextEpisode = serializers.SerializerMethodField(method_name='getNextEpisode', read_only=True)
    liking = serializers.SerializerMethodField(method_name='isLiking', read_only=True)
    imageUrl = serializers.SerializerMethodField(method_name='getImageUrl', read_only=True)
    class Meta:
        model = Episode
        fields = ['id', 'title', 'episodeNumber', 'totalRating', 'releasedDate', 'webtoon', 'previousEpisode', 'nextEpisode', 'liking', 'likedBy', 'imageUrl']
        
        read_only_fields = ['totalRating', 'releasedDate', 'previousEpisode', 'nextEpisode', 'liking', 'likedBy']

    
    def update(self, instance, validated_data):
        for key in validated_data:
            if key in ['webtoon']:
                continue
            setattr(instance, key, validated_data[key])
        webtoon = validated_data.get('webtoon', instance.webtoon)
        if not isinstance(webtoon, Webtoon):
            instance.webtoon = Webtoon.objects.get(title=webtoon['title'])
        instance.save()
        instance.webtoon.update_rating()
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

    def getImageUrl(self, obj):
        return settings.S3_URL + "/img/" + str(obj.webtoon.id) + "/" + str(obj.episodeNumber)
    


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


class UserProfileSerializer(serializers.ModelSerializer):
    """유저 Serializer"""
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




# class CommentInfoSerializer(serializers.ModelSerializer):
#     """Webtoon 페이지에서 보여지는 Comment의 Serializer"""
#     class Meta:
#         model = Comment
#         fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy']
#         read_only_fields = ['dtCreated', 'dtUpdated', 'createdBy']



class CommentContentSerializer(serializers.ModelSerializer):
    """댓글 페이지 안에서의 Serializer"""
    # comments = CommentInfoSerializer(many=True, read_only=True)
    subComments = serializers.SerializerMethodField(method_name='getComments', read_only=True)
    createdBy = UserInfoSerializer(read_only=True)
    liking = serializers.SerializerMethodField(method_name='isLiking', read_only=True)
    disiking = serializers.SerializerMethodField(method_name='isDisliking', read_only=True)

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




    # def create(self, validated_data):
    #     instance = Comment()
    #     for key in validated_data:
    #         if key in ['comments', 'likedBy', 'dislikedBy']:
    #             continue
    #         setattr(instance, key, validated_data[key])
    #     likedBy = validated_data.get('likedBy', instance.likedBy)
    #     if hasattr(likedBy, '__iter__'):
    #         for user in instance.likedBy.all():
    #             instance.likedBy.remove(user)
    #         for user in likedBy:
    #             print(user)
    #             instance.likedBy.add(User.objects.get(nickname=user.nickname))
    #
    #     dislikedBy = validated_data.get('dislikedBy', instance.dislikedBy)
    #     if hasattr(dislikedBy, '__iter__'):
    #         for user in instance.dislikedBy.all():
    #             instance.dislikedBy.remove(user)
    #         for user in dislikedBy:
    #             print(user)
    #             instance.dislikedBy.add(User.objects.get(nickname=user.nickname))
    #     instance.save()
    #     return instance


    # def update(self, instance, validated_data):
    #     for key in validated_data:
    #         if key in ['comments', 'likedBy', 'dislikedBy']:
    #             continue
    #         setattr(instance, key, validated_data[key])
    #     likedBy = validated_data.get('likedBy', instance.likedBy)
    #     if hasattr(likedBy, '__iter__'):
    #         for user in instance.likedBy.all():
    #             instance.likedBy.remove(user)
    #         for user in likedBy:
    #             instance.likedBy.add(User.objects.get(nickname=user.nickname))
    #
    #
    #     dislikedBy = validated_data.get('dislikedBy', instance.dislikedBy)
    #     if hasattr(dislikedBy, '__iter__'):
    #         for user in instance.dislikedBy.all():
    #             instance.dislikedBy.remove(user)
    #         for user in dislikedBy:
    #             instance.dislikedBy.add(User.objects.get(nickname=user.nickname))
    #     instance.save()
    #     return instance
    #
    # def validate(self, data):
    #     return data
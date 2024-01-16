from django.http import Http404

from user.models import User
from rest_framework import serializers

from .models import DayOfWeek, Webtoon, Episode, Comment, Tag
from user.serializers import UserSerializer


# ///////////////////////////////////////////////////////////////////////////////
# Serializer 작업 때 Image 관련 요소 모두 주석처리 하여 추후 Merge 때 확인 필요
# ///////////////////////////////////////////////////////////////////////////////




class TagSerializer(serializers.ModelSerializer):
    """태그 Serializer"""
    class Meta:
        model = Tag
        fields = ['content']

    def run_validation(self, data):
        try:
            value = Tag.objects.get(pk=data['content'])
        except:
            value = Tag.objects.create(pk=data['content'])
        return value


class DayOfWeekSerializer(serializers.ModelSerializer):
    """요일 Serializer"""
    class Meta:
        model = DayOfWeek
        fields = ['name']



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
    uploadDays = DayOfWeekSerializer(many=True)
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer(read_only = True)
    subscribeCount = serializers.SerializerMethodField(method_name='getSubscribeCount')
    class Meta:
        model = Webtoon
        fields = ['id', 'title', 'description', 'uploadDays', 'author', 'totalRating', 'tags', 'subscribeCount']
        #fields = ['id', 'title', 'titleImage', 'description', 'uploadDays', 'author', 'totalRating', 'tags']
        read_only_fields = ['author', 'releasedDate', 'subscribeCount', 'totalRating']
       
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
        tags = validated_data.get('tags', instance.tags)
        if hasattr(tags, '__iter__'):
            for tag in instance.tags.all():
                instance.tags.remove(tag)
            for tag in tags:
                instance.tags.add(tag)
        instance.update_rating()
        instance.save()
        return instance

    def getSubscribeCount(self, obj):
        return obj.subscribers.count()
    

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


class UserContentSerializer(serializers.ModelSerializer):
    """유저 Serializer"""
    webtoons = WebtoonInfoSerializer(many=True)
    subscribingWebtoons = WebtoonInfoSerializer(many=True)
    subscribers = SubscriberUserSerializer(many=True)
    class Meta:
        model = User
        fields = ['id', 'nickname', 'isAuther', 'webtoons', 'subscribingWebtoons', 'subscribers']




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
    # likedBy = UserInfoSerializer(many=True)
    likedBy = serializers.SerializerMethodField(method_name='getLikedBy', read_only=True)
    # dislikedBy = UserInfoSerializer(many=True)
    dislikedBy = serializers.SerializerMethodField(method_name='getDislikedBy', read_only=True)
    createdBy = UserInfoSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy', 'subComments', 'likedBy', 'dislikedBy']
        read_only_fields = ['dtCreated', 'dtUpdated', 'createdBy', 'subComments', 'likedBy', 'dislikedBy']

    def getComments(self, obj):
        return obj.comments.count()

    def getLikedBy(self, obj):
        return obj.likedBy.count()

    def getDislikedBy(self, obj):
        return obj.dislikedBy.count()
    

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


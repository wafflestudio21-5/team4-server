from user.models import User
from rest_framework import serializers
from .models import DayOfWeek, Webtoon, Episode, Comment, Tag


# ///////////////////////////////////////////////////////////////////////////////
# Serializer 작업 때 Image 관련 요소 모두 주석처리 하여 추후 Merge 때 확인 필요
# ///////////////////////////////////////////////////////////////////////////////


class TagSerializer(serializers.ModelSerializer):
    """태그 Serializer"""
    class Meta:
        model = Tag
        fields = ['content']

    def run_validation(self, data):
        value = Tag.objects.get(pk=data['content'])
        return value


class DayOfWeekSerializer(serializers.ModelSerializer):
    """요일 Serializer"""
    class Meta:
        model = DayOfWeek
        fields = ['name']


class WebtoonInfoSerializer(serializers.ModelSerializer):
    """Webtoon 리스트에서 보여지는 Webtoon의 Serializer"""
    class Meta:
        model = Webtoon
        #fields = ['id', 'title', 'titleImage']
        fields = ['id', 'title']


class WebtoonContentSerializer(serializers.ModelSerializer):
    """Webtoon 페이지 안에서의 Serializer"""
    uploadDays = DayOfWeekSerializer(many=True)
    tags = TagSerializer(many=True, required=False)
    class Meta:
        model = Webtoon
        fields = ['id', 'title', 'description', 'uploadDays', 'author', 'totalRating', 'tags']
        #fields = ['id', 'title', 'titleImage', 'description', 'uploadDays', 'author', 'totalRating', 'tags']
    

    def update(self, instance, validated_data):
        for key in validated_data:
            if key in ['uploadDays', 'tags']:
                continue
            setattr(instance, key, validated_data[key])
        print(validated_data)
        uploadDays = validated_data.get('uploadDays', instance.uploadDays)
        if hasattr(uploadDays, '__iter__'):
            for uploadDay in instance.uploadDays.all():
                instance.uploadDays.remove(uploadDay)
            for uploadDay in uploadDays:
                instance.uploadDays.add(DayOfWeek.objects.get(name=uploadDay['name']))

        tags = validated_data.get('tags', instance.tags)
        if hasattr(tags, '__iter__'):
            for tag in instance.tags.all():
                instance.tags.remove(tag)
            for tag in tags:
                instance.tags.add(tag)
        instance.update_rating()
        instance.save()
        return instance
    
 

class EpisodeInfoSerializer(serializers.ModelSerializer):
    """Webtoon 페이지에서 보여지는 Episode의 Serializer"""
    class Meta:
        model = Episode
        fields = ['id', 'title', 'episodeNumber', 'thumbnail', 'rating', 'releasedDate']


class EpisodeContentSerializer(serializers.ModelSerializer):
    """Episode 페이지 안에서의 Serializer"""
    webtoon = WebtoonInfoSerializer(read_only=True)
    class Meta:
        model = Episode
        #fields = ['id', 'title', 'content', 'rating', 'webtoon']
        fields = ['id', 'title', 'rating', 'webtoon']
    
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


class CommentInfoSerializer(serializers.ModelSerializer):
    """Webtoon 페이지에서 보여지는 Comment의 Serializer"""
    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy']
        extra_kwargs = {'createdBy' : {'read_only' : True}}


class CommentContentSerializer(serializers.ModelSerializer):
    """댓글 페이지 안에서의 Serializer"""
    comments = CommentInfoSerializer(many=True, read_only=True)
    likedBy = UserInfoSerializer(many=True)
    dislikedBy = UserInfoSerializer(many=True)
    class Meta:
        model = Comment
        fields = ['id', 'content', 'dtCreated', 'dtUpdated', 'createdBy', 'comments', 'likedBy', 'dislikedBy']
        extra_kwargs = {'createdBy' : {'read_only' : True}}
    
    def create(self, validated_data):
        instance = Comment()
        for key in validated_data:
            if key in ['comments', 'likedBy', 'dislikedBy']:
                continue
            setattr(instance, key, validated_data[key])
        likedBy = validated_data.get('likedBy', instance.likedBy)
        if hasattr(likedBy, '__iter__'):
            for user in instance.likedBy.all():
                instance.likedBy.remove(user)
            for user in likedBy:
                print(user)
                instance.likedBy.add(User.objects.get(nickname=user.nickname))

        dislikedBy = validated_data.get('dislikedBy', instance.dislikedBy)
        if hasattr(dislikedBy, '__iter__'):
            for user in instance.dislikedBy.all():
                instance.dislikedBy.remove(user)
            for user in dislikedBy:
                print(user)
                instance.dislikedBy.add(User.objects.get(nickname=user.nickname))  
        instance.save()
        return instance


    def update(self, instance, validated_data):
        for key in validated_data:
            if key in ['comments', 'likedBy', 'dislikedBy']:
                continue
            setattr(instance, key, validated_data[key])
        likedBy = validated_data.get('likedBy', instance.likedBy)
        if hasattr(likedBy, '__iter__'):
            for user in instance.likedBy.all():
                instance.likedBy.remove(user)
            for user in likedBy:
                print(user)
                instance.likedBy.add(User.objects.get(nickname=user.nickname))

        dislikedBy = validated_data.get('dislikedBy', instance.dislikedBy)
        if hasattr(dislikedBy, '__iter__'):
            for user in instance.dislikedBy.all():
                instance.dislikedBy.remove(user)
            for user in dislikedBy:
                print(user)
                instance.dislikedBy.add(User.objects.get(nickname=user.nickname))  
        instance.save()
        return instance

    def validate(self, data):
        return data
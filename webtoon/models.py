from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from user.models import User
from .validators import isDayName


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # profileImage = models.ImageField()
    introduction = models.CharField(max_length=200, blank=True, null=True)
    isAuthor = models.BooleanField(default=False)
    
    subscribers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='subscribingAuthors') # 구독자

    def __str__(self):
        return self.user.nickname


class DayOfWeek(models.Model):
    """요일 모델 : 요일별 웹툰 분류를 위해 사용"""
    # 요일 이름 : Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    name = models.CharField(max_length=10, validators=[isDayName], unique=True)

    def __str__(self):
        return self.name


class Webtoon(models.Model):
    """웹툰 모델"""
    title = models.CharField(max_length=50)
    #titleImage = models.ImageField()
    description = models.CharField(max_length=200)
    isFinished = models.BooleanField(default=False)
    totalRating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    uploadDays = models.ManyToManyField(DayOfWeek, blank=False, related_name='webtoons')    # 업로드 요일 (복수 선택가능)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploadedWebtoons')
    subscribers = models.ManyToManyField(User, blank=True, related_name='subscribingWebtoons')   # 구독자
    releasedDate = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.title

    def update_rating(self):
        rating = 0.0
        for episode in self.episodes.all():
            rating += float(episode.rating)
        if self.episodes.count() != 0:
            rating /= self.episodes.count()
        self.totalRating = rating
        self.save()


class Episode(models.Model):
    """회차 모델"""
    title = models.CharField(max_length=50)
    episodeNumber = models.IntegerField()                                # 회차 번호
    #thumbnail = models.ImageField()
    #content = models.ImageField()

    totalRating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    releasedDate = models.DateField(auto_now_add=True)

    webtoon = models.ForeignKey(Webtoon, on_delete=models.CASCADE, related_name='episodes')

    comments = GenericRelation('Comment', related_query_name='episode')
    likes = GenericRelation('Like', related_query_name='episode')
    
    # 좋아요, 싫어요
    likedBy = models.PositiveIntegerField(default=0)
    dislikedBy = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['webtoon', 'episodeNumber']

    def __str__(self):
        return str(self.episodeNumber) + '. ' + self.title

    def update_rating(self):
        rating = 0.0
        for episode in self.episodes.all():
            rating += float(episode.rating)
        if self.episodes.count() != 0:
            rating /= self.episodes.count()
        self.totalRating = rating
        self.save()


class Comment(models.Model):
    """댓글 모델"""
    content = models.CharField(max_length=300)
    dtCreated = models.DateTimeField(auto_now_add=True)
    dtUpdated = models.DateTimeField(auto_now=True)

    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    # generic relationship ( 댓글을 회차에 달거나, 댓글에 대댓글로 달 수 있으므로 )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    commentOn = GenericForeignKey()                           # 어떤 회차, 혹은 댓글에 달린 댓글인지

    comments = GenericRelation('Comment')                     # 본 댓글에 달린 대댓글들

    likes = GenericRelation('Like', related_query_name='comment')

    # 좋아요, 싫어요
    likedBy = models.PositiveIntegerField(default=0)
    dislikedBy = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.content[:30]


class Tag(models.Model):
    """태그 모델"""
    content = models.CharField(max_length=20, primary_key=True, unique=True)
    webtoons = models.ManyToManyField(Webtoon, blank=True, related_name='tags')

    def __str__(self):
        return self.content
    

class Rating(models.Model):
    """평점 모델"""
    rating = models.PositiveIntegerField()
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    ratingOn = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='ratings', blank=True, null=True)

    class Meta:
        unique_together = ['createdBy', 'ratingOn']


class Like(models.Model):
    """좋아요/싫어요 모델"""
    isLike = models.BooleanField()
    isDislike = models.BooleanField()
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    # generic relationship 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    likeOn = GenericForeignKey()                           # 어떤 회차, 혹은 댓글에 대한 좋아요인지

    class Meta:
        unique_together = ['createdBy', 'content_type', 'object_id']
                     
from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import generics 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


from .models import Webtoon, Comment, DayOfWeek, Episode, Tag, UserProfile 
from .serializers import (WebtoonContentSerializer,
                          WebtoonInfoSerializer,
                          WebtoonContentSerializer,
                          TagSerializer,
                          EpisodeInfoSerializer,
                          EpisodeContentSerializer,
                          CommentInfoSerializer,
                          CommentContentSerializer,
                          SubscriberUserProfileSerializer,)



# Create your views here.

# Webtoon 하나하나를 보여주는 View
class WebtoonAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Webtoon.objects.all()
    serializer_class  = WebtoonContentSerializer

    # Webtoon이 delete 될 때, 만약 대응되는 tag가 하나도 남지 않게 된다면 tag를 delete. 
    def delete(self, request, pk):
        webtoon = self.get_object()
        for tag in webtoon.tags.all():
            if tag.webtoons.count() == 1:
                tag.delete()
        return super().delete(request, pk)


# Episode 하나하나를 보여주는 View
class EpisodeAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Episode.objects.all()
    serializer_class = EpisodeContentSerializer


# Comment 하나하나를 보여주는 View
class CommentAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentContentSerializer
    allow_data_on_creating = ['content']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def post(self, request, pk):
        if self.get_object().content_type == ContentType.objects.get(model='comment'):
            return Response({'message': 'Comment on comment is not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        for key in request.data:
            if key not in self.allow_data_on_creating:
                return Response({'message' : 'To create comments, only these data should be entered : ' + str(self.allow_data_on_creating)}, status=status.HTTP_400_BAD_REQUEST)
        instance = Comment.objects.create(createdBy=request.user, commentOn=self.get_object())
        request.data['likedBy'] = []
        request.data['dislikedBy'] = []
        serializer = CommentContentSerializer(data=request.data, instance=instance)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()




class WebtoonListAPIView(APIView):
    def get(self, request):
        queryset = Webtoon.objects.all()
        serializer = WebtoonInfoSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if "tags" not in request.data :
            request.data['tags'] = []

        serializer = WebtoonContentSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class WebtoonListFinishedAPIView(generics.ListAPIView):
    queryset = Webtoon.objects.filter(isFinished=True)
    serializer_class = WebtoonInfoSerializer

class WebtoonListRecentAPIView(generics.ListAPIView):
    serializer_class = WebtoonInfoSerializer

    def get_queryset(self):
        from datetime import date, timedelta
        today = date.today()
        return Webtoon.objects.filter(releasedDate__gte=today - timedelta(21))

class DayWebtoonListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = WebtoonInfoSerializer

    def get_queryset(self):
        day = get_object_or_404(DayOfWeek, name=self.kwargs.get('day'))
        return Webtoon.objects.filter(uploadDays=day)

class EpisodeListAPIView(APIView):
    def getWebtoon(self, pk):
        return Webtoon.objects.get(pk = pk)

    def get(self, request, pk):
        webtoon = self.getWebtoon(pk)
        queryset = Episode.objects.filter(webtoon=webtoon)
        serializer = EpisodeInfoSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        webtoon = self.getWebtoon(pk)
        serializer = EpisodeContentSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(webtoon=webtoon)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class TagWebtoonAPIView(APIView):
    def getTag(self, pk):
        return Tag.objects.get(pk = pk)

    def get(self, request, content):
        tag = self.getTag(content)
        queryset = Webtoon.objects.filter(tags=tag)
        serializer = WebtoonInfoSerializer(queryset, many=True)
        return Response(serializer.data)
    

class EpisodeCommentAPIView(APIView):
    def getEpisode(self, pk):
        return Episode.objects.get(pk = pk)
    
    def getContentType(self):
        return ContentType.objects.get(model="comment")

    def get(self, request, pk):
        episode = self.getEpisode(pk)
        queryset = Comment.objects.filter(object_id=pk).filter(content_type=self.getContentType())
        serializer = CommentInfoSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        episode = self.getEpisode(pk)
        if 'likedBy' not in request.data:
            request.data['likedBy'] = []
        if 'dislikedBy' not in request.data:
            request.data['dislikedBy'] = []

        serializer = CommentContentSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            comment = serializer.save(createdBy = request.user, 
                                      content_type = self.getContentType(),
                                      object_id = pk)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

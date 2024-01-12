from django.shortcuts import render, get_object_or_404

from .models import Webtoon, Comment, DayOfWeek, Episode, Tag, UserProfile 
from .serializers import (WebtoonInfoSerializer,
                          WebtoonContentSerializer,
                          TagSerializer,
                          EpisodeInfoSerializer,
                          EpisodeContentSerializer,
                          CommentInfoSerializer,
                          CommentContentSerializer,
                          SubscriberUserProfileSerializer,)

from rest_framework import generics 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

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
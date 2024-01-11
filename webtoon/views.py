from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response



from .models import Webtoon, Episode, Comment, UserProfile
from .serializers import WebtoonContentSerializer, EpisodeContentSerializer, CommentInfoSerializer, CommentContentSerializer


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
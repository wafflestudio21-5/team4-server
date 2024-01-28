from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.db.models import Subquery, OuterRef

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import generics 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import filters
from django.contrib.contenttypes.models import ContentType

from user.models import User

from .models import Webtoon, Comment, DayOfWeek, Episode, Tag, UserProfile 
from .serializers import (WebtoonContentSerializer,
                          WebtoonInfoSerializer,
                          WebtoonContentSerializer,
                          EpisodeInfoSerializer,
                          EpisodeContentSerializer,
                          # CommentInfoSerializer,
                          CommentContentSerializer,
                          DayOfWeekSerializer
                          )
from .permissions import (IsAuthorOrReadOnly,
                          IsWebtoonAuthorOrReadOnly,
                          IsEpisodeAuthorOrReadOnly,
                          IsEpisodeWebtoonAuthorOrReadOnly,
                          IsCommentAuthorOrReadOnly,
                          )
from .validators import isDayName
from .paginations import (CommentCursorPagination,
                          WebtoonCursorPagination,
                          PaginationHandlerMixin,
                          EpisodeCursorPagination,
                          )

from imageUploader import S3ImageUploader

def annotateLatestUploadDate(queryset):
    """Webtoon queryset을 가장 최근 에피소드 업로드 순으로 정렬"""
    queryset = queryset.annotate(
        latestUploadDate=Subquery(
            Episode.objects.filter(
                webtoon_id=OuterRef('pk')
            ).order_by('-releasedDate').values('releasedDate')[0]
        )
    )

    return queryset


# Create your views here.

# Webtoon 하나하나를 보여주는 View
class WebtoonAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsWebtoonAuthorOrReadOnly,)
    queryset = Webtoon.objects.all()
    serializer_class = WebtoonContentSerializer

    # Webtoon이 update 또는 delete 될 때, 만약 대응되는 tag가 하나도 남지 않게 된다면 tag를 delete.
    def perform_update(self, serializer):
        if 'tags' in serializer.validated_data:
            formerTags = self.get_object().tags.all()
            newTags = serializer.validated_data.get('tags')
            for formerTag in formerTags:
                if (formerTag not in newTags) and (formerTag.webtoons.count() == 1):
                    formerTag.delete()

        # 요일 이름 체크
        if 'uploadDays' in serializer.validated_data:
            for day in serializer.validated_data.get('uploadDays'):
                if not isDayName(day.get('name')):
                    raise Http404("Day name not found")

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        webtoon = self.get_object()
        for tag in webtoon.tags.all():
            if tag.webtoons.count() == 1:
                tag.delete()

        #TODO : titleImage 삭제 기능 구현 필요
        
        super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(status=200)
    
    def update(self, request, *args, **kwargs):
        image = request.FILES['titleImage']
        try :
            url = S3ImageUploader(image, request.data['title']).upload()
        except:
            return Response({"error" : "Wrong Image Request"}, status=400)
        kwargs += {"titleImage" : url}
        
        return super().update(request, *args, **kwargs)


# Episode 하나하나를 보여주는 View
class EpisodeAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, IsEpisodeAuthorOrReadOnly,)
    queryset = Episode.objects.all()
    serializer_class = EpisodeContentSerializer

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(status=200)


class SubCommentListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentContentSerializer
    pagination_class = CommentCursorPagination

    def get_comment(self):
        """상위 댓글 가져오기"""
        return get_object_or_404(Comment, pk=self.kwargs.get('pk'))

    def get_queryset(self):
        comment = self.get_comment()
        return comment.comments.all()

    def perform_create(self, serializer):
        createdBy = self.request.user
        commentOn = self.get_comment()
        serializer.save(createdBy=createdBy, commentOn=commentOn)


# Comment 하나하나를 보여주는 View
class CommentAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentAuthorOrReadOnly,]
    queryset = Comment.objects.all()
    serializer_class = CommentContentSerializer
    # allow_data_on_creating = ['content']
    # http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    # def post(self, request, pk):
    #     # 대댓글에 대댓글을 달려고 할 시 error return
    #     if self.get_object().content_type == ContentType.objects.get(model='comment'):
    #         return Response({'message': 'Comment on subcomment is not allowed'}, status=status.HTTP_400_BAD_REQUEST)
    #     # content 제외한 데이터 입력 시 error return
    #     for key in request.data:
    #         if key not in self.allow_data_on_creating:
    #             return Response({'message' : 'To create comments, only these data should be entered : ' + str(self.allow_data_on_creating)}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     instance = Comment.objects.create(createdBy=request.user, commentOn=self.get_object())
    #     if 'likedBy' not in request.data:
    #         request.data['likedBy'] = []
    #     if 'dislikedBy' not in request.data:
    #         request.data['dislikedBy'] = []
    #     serializer = CommentContentSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     # instance.delete()
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()


class WebtoonListAPIView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = WebtoonCursorPagination
    serializer_class = WebtoonContentSerializer

    def get_queryset(self):
        queryset = Webtoon.objects.all()
        # 최근 업로드 에피소드의 업로드 시간 기준 정렬
        # return annotateLatestUploadDate(queryset)
        return queryset

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request):
        instance = self.get_queryset()

        serializer_class = WebtoonInfoSerializer
        kwargs = {'context': self.get_serializer_context()}

        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(serializer_class(page, many=True, **kwargs).data)
        else:
            serializer = WebtoonInfoSerializer(instance, many=True, **kwargs)
        return Response(serializer.data)

    def post(self, request):
        if "tags" not in request.data :
            request.data['tags'] = []

        image = request.FILES['titleImage']
        try :
            url = S3ImageUploader(image, request.data['title']).upload()
        except:
            return Response({"error" : "Wrong Image Request"}, status=400)
        
        kwargs = {'context': self.get_serializer_context(),
                  'titleImage' : url}

        serializer = WebtoonContentSerializer (data = request.data, **kwargs)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class WebtoonListFinishedAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = WebtoonInfoSerializer
    pagination_class = WebtoonCursorPagination

    def get_queryset(self):
        queryset = Webtoon.objects.filter(isFinished=True)
        # 최근 업로드 에피소드의 업로드 시간 기준 정렬
        # return orderByLatestEpisode(queryset)
        return queryset


class WebtoonListRecentAPIView(generics.ListAPIView):
    permission_class = [IsAuthenticatedOrReadOnly]
    serializer_class = WebtoonInfoSerializer
    pagination_class = WebtoonCursorPagination

    def get_queryset(self):
        from datetime import date, timedelta
        today = date.today()
        queryset = Webtoon.objects.filter(releasedDate__gte=today - timedelta(21))
        # return orderByLatestEpisode(queryset)
        return queryset


class DayWebtoonListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = WebtoonInfoSerializer
    pagination_class = WebtoonCursorPagination

    def get_queryset(self):
        day = get_object_or_404(DayOfWeek, name=self.kwargs.get('day'))
        queryset = Webtoon.objects.filter(uploadDays=day)
        # return orderByLatestEpisode(queryset)
        return queryset


class EpisodeListAPIView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAuthenticatedOrReadOnly, IsEpisodeWebtoonAuthorOrReadOnly]
    pagination_class = EpisodeCursorPagination
    serializer_class = EpisodeContentSerializer

    def getWebtoon(self, pk):
        return get_object_or_404(Webtoon, pk=pk)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get(self, request, pk):
        webtoon = self.getWebtoon(pk)
        instance = Episode.objects.filter(webtoon=webtoon)
        kwargs = {'context': self.get_serializer_context()}
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(EpisodeInfoSerializer(page, many=True, **kwargs).data)
        else:
            serializer = EpisodeInfoSerializer(instance, many=True, **kwargs)
        return Response(serializer.data)

    def post(self, request, pk):
        webtoon = self.getWebtoon(pk)
        kwargs = {'context': self.get_serializer_context()}
        serializer = EpisodeContentSerializer(data = request.data, **kwargs)
        if serializer.is_valid(raise_exception=True):
            serializer.save(webtoon=webtoon)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class TagWebtoonAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = WebtoonInfoSerializer
    pagination_class = WebtoonCursorPagination

    def getTag(self, pk):
        return Tag.objects.get(pk = pk)

    def get_queryset(self):
        tag = self.getTag(self.kwargs.get('content'))
        queryset = Webtoon.objects.filter(tags=tag)
        # return orderByLatestEpisode(queryset)
        return queryset

    # def get(self, request, content):
    #     tag = self.getTag(content)
    #     queryset = Webtoon.objects.filter(tags=tag)
    #     serializer = WebtoonInfoSerializer(queryset, many=True)
    #     return Response(serializer.data)
    

# class EpisodeCommentAPIView(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     allow_data_on_creating = ['content']
#
#     def getEpisode(self, pk):
#         return get_object_or_404(Episode, pk=pk)
#
#     def getContentType(self):
#         return ContentType.objects.get(model="episode")
#
#     def get(self, request, pk):
#         episode = self.getEpisode(pk)
#         queryset = Comment.objects.filter(object_id=pk).filter(content_type=self.getContentType())
#         serializer = CommentInfoSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, pk):
#         for key in request.data:
#             if key not in self.allow_data_on_creating:
#                 return Response({'message' : 'To create comments, only these data should be entered : ' + str(self.allow_data_on_creating)}, status=status.HTTP_400_BAD_REQUEST)
#         instance = Comment.objects.create(createdBy=request.user, commentOn=self.getEpisode(pk))
#         if 'likedBy' not in request.data:
#             request.data['likedBy'] = []
#         if 'dislikedBy' not in request.data:
#             request.data['dislikedBy'] = []
#         serializer = CommentContentSerializer(data=request.data, instance=instance)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class EpisodeCommentAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentContentSerializer
    pagination_class = CommentCursorPagination

    def get_episode(self):
        return get_object_or_404(Episode, pk=self.kwargs.get('pk'))

    def get_queryset(self):
        episode = self.get_episode()
        return Comment.objects.filter(episode=episode)

    def perform_create(self, serializer):
        createdBy = self.request.user
        commentOn = self.get_episode()
        serializer.save(createdBy=createdBy, commentOn=commentOn)


class UploadWebtoonListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = WebtoonInfoSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        queryset = Webtoon.objects.filter(author=user)
        # return orderByLatestEpisode(queryset)
        return queryset


class WebtoonSubscribeAPIView(APIView):
    def post(self, request, pk):
        webtoon = get_object_or_404(Webtoon, pk=pk)
        if request.user.subscribingWebtoons.filter(pk=webtoon.pk).exists():
            webtoon.subscribers.remove(request.user)
        else:
            webtoon.subscribers.add(request.user)
        return Response(status=status.HTTP_200_OK)


class SubscribeWebtoonListAPIView(generics.ListAPIView):
    serializer_class = WebtoonInfoSerializer

    def get_queryset(self):
        queryset = Webtoon.objects.filter(subscribers=self.request.user)
        # return orderByLatestEpisode(queryset)
        return queryset


class WebtoonSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Webtoon.objects.all()
    serializer_class = WebtoonInfoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
        

class DayOfWeekCreateAPIView(generics.CreateAPIView):
    serializer_class = DayOfWeekSerializer

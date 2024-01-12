from django.urls import path

from .views import (WebtoonAPIView, 
                    EpisodeAPIView, 
                    CommentAPIView
                    WebtoonListAPIView,
                    WebtoonListFinishedAPIView,
                    WebtoonListRecentAPIView,
                    DayWebtoonListAPIView,
                    EpisodeListAPIView,
                    TagWebtoonAPIView,
                    EpisodeCommentAPIView,
                   )

urlpatterns = [
    path('api/webtoonList', WebtoonListAPIView.as_view()), 
    path('api/webtoonList/finished', WebtoonListFinishedAPIView.as_view()), 
    path('api/webtoonList/recent', WebtoonListRecentAPIView.as_view()), 
    path('api/webtoonList/<str:day>', DayWebtoonListAPIView.as_view()), 
    path('api/webtoon/<int:pk>', WebtoonAPIView.as_view()), 
    path('api/webtoon/<int:pk>/episode', EpisodeListAPIView.as_view()), 
    path('api/episode/<int:pk>', EpisodeAPIView.as_view()), 
    path('api/episode/<int:pk>/comment', EpisodeCommentAPIView.as_view()),
    path('api/comment/<int:pk>', CommentAPIView.as_view()), 
    path('api/tag/<str:content>', TagWebtoonAPIView.as_view()), 

]
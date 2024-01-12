from django.urls import path
from .views import (WebtoonListAPIView,
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
    #path('api/webtoon/<int:pk>', ), 
    path('api/webtoon/<int:pk>/episode', EpisodeListAPIView.as_view()), 
    #path('api/episode/<int:pk>', ), 
    path('api/episode/<int:pk>/comment', EpisodeCommentAPIView.as_view()),
    #path('api/comment/<int:pk>', ), 
    path('api/tag/<str:content>', TagWebtoonAPIView.as_view()),   
]
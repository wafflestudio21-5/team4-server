from django.urls import path

from .views import (WebtoonAPIView,
                    WebtoonSubscribeAPIView,
                    EpisodeAPIView, 
                    CommentAPIView, 
                    WebtoonListAPIView,
                    WebtoonListFinishedAPIView,
                    WebtoonListRecentAPIView,
                    DayWebtoonListAPIView,
                    EpisodeListAPIView,
                    TagWebtoonAPIView,
                    EpisodeCommentAPIView,
                    
                    # new views
                    SubCommentListAPIView,
                    UploadWebtoonListAPIView,
                    SubscribeWebtoonListAPIView,
                    WebtoonSearchView,
                    DayOfWeekCreateAPIView,
                    EpisodeRatingAPIView, 
                    EpisodeLikeAPIView, 
                    CommentLikeAPIView, 
                    UserProfileAPIView,
                    AuthorSubscribeAPIView,
                    SubscribeAuthorListAPIView,
                    #EpisodeThumnailAPIView,
                    WebtoonTitleImageAPIView,
                    EpisodeImageListAPIView,
                   )

urlpatterns = [
    path('api/webtoonList', WebtoonListAPIView.as_view()), 
    path('api/webtoonList/finished', WebtoonListFinishedAPIView.as_view()), 
    path('api/webtoonList/recent', WebtoonListRecentAPIView.as_view()),
    path('api/webtoonList/search', WebtoonSearchView.as_view()),
    path('api/webtoonList/<str:day>', DayWebtoonListAPIView.as_view()),
    path('api/webtoon/<int:pk>', WebtoonAPIView.as_view()), 
    path('api/webtoon/<int:pk>/titleImage', WebtoonTitleImageAPIView.as_view()), 
    path('api/webtoon/<int:pk>/episode', EpisodeListAPIView.as_view()),
    path('api/webtoon/<int:pk>/subscribe', WebtoonSubscribeAPIView.as_view()),
    path('api/episode/<int:pk>', EpisodeAPIView.as_view()), 
    #path('api/episode/<int:pk>/thumbnail', EpisodeThumnailAPIView.as_view()), 
    path('api/episode/<int:pk>/comment', EpisodeCommentAPIView.as_view()),
    path('api/comment/<int:pk>', CommentAPIView.as_view()),
    path('api/tag/<str:content>', TagWebtoonAPIView.as_view()),

    # new endpoints
    path('api/comment/<int:pk>/comment', SubCommentListAPIView.as_view()),

    path('api/profile/<int:pk>', UserProfileAPIView.as_view()),
    path('api/profile/<int:pk>/subscribe', AuthorSubscribeAPIView.as_view()),
    path('api/profile/<int:pk>/uploadWebtoonList', UploadWebtoonListAPIView.as_view()),
    path('api/subscribeAuthorList', SubscribeAuthorListAPIView.as_view()),
    path('api/subscribeWebtoonList', SubscribeWebtoonListAPIView.as_view()),

    path('api/episode/<int:pk>/rating', EpisodeRatingAPIView.as_view()), 
    path('api/episode/<int:pk>/like', EpisodeLikeAPIView.as_view()), 
    path('api/comment/<int:pk>/like', CommentLikeAPIView.as_view()), 

    path('api/episode/<int:pk>/images', EpisodeImageListAPIView.as_view()),
    # 임시 엔드포인트
    # path('api/dayofweek', DayOfWeekCreateAPIView.as_view())
]
from django.urls import path
from .views import WebtoonAPIView, EpisodeAPIView, CommentAPIView

urlpatterns = [
    #path('api/webtoonList', ), 
    #path('api/webtoonList/finished', ), 
    #path('api/webtoonList/recent', ), 
    #path('api/webtoonList/<std:day>', ), 
    path('api/webtoon/<int:pk>', WebtoonAPIView.as_view()), 
    #path('api/webtoon/<int:pk>/episode', ), 
    path('api/episode/<int:pk>', EpisodeAPIView.as_view()), 
    #path('api/episode/<int:pk>/comment', ),
    path('api/comment/<int:pk>', CommentAPIView.as_view()), 
    #path('api/tag/<int:pk>', ),   
]
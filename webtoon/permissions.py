from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Webtoon


class IsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.profile.isAuthor


class IsWebtoonAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.author


class IsEpisodeAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.webtoon.author


class IsEpisodeWebtoonAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        webtoonPk = view.kwargs.get('pk')
        try:
            webtoon = Webtoon.objects.get(pk=webtoonPk)
        except Webtoon.DoesNotExist:
            return False
        return webtoon.author == request.user


class IsCommentAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.createdBy


class IsProfileUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.user

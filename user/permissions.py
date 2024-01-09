from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class IsNotAuthenticated(BasePermission):
    """
    Allows access only to non-authenticated users.
    """

    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            raise PermissionDenied("You cannot register when you are already authenticated")
        return True
class CustomIsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            raise PermissionDenied("You cannot logout when you are not authenticated")
        return True
        

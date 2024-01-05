from django.urls import path
from .views import AuthAPIView, SignupAPIView

urlpatterns = [
    # auth
    path('auth/', AuthAPIView.as_view(), name="account-auth"),
    path('registration/', SignupAPIView.as_view(), name='account-signup'),
]
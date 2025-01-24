from django.urls import path

from .views import UserProfileUpdateView, UserRegistrationView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('user/profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
]



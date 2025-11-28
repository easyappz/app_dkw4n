from django.urls import path
from .views import (
    HelloView,
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    ProfileView,
    ReferralLinkView
)

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),
    
    # Authentication endpoints
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("auth/me", MeView.as_view(), name="me"),
    
    # User endpoints
    path("users/profile", ProfileView.as_view(), name="profile"),
    path("users/referral-link", ReferralLinkView.as_view(), name="referral-link"),
]

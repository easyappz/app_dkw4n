from django.urls import path
from .views import (
    HelloView,
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    ProfileView,
    ReferralLinkView,
    ReferralsListView,
    ReferralStatsView,
    ReferralTreeView,
    TransactionsListView,
    DepositView,
    BonusesListView,
    CurrentLevelView,
    LevelsListView
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
    
    # Referral endpoints
    path("referrals", ReferralsListView.as_view(), name="referrals-list"),
    path("referrals/stats", ReferralStatsView.as_view(), name="referral-stats"),
    path("referrals/tree", ReferralTreeView.as_view(), name="referral-tree"),
    
    # Transaction endpoints
    path("transactions", TransactionsListView.as_view(), name="transactions-list"),
    path("transactions/deposit", DepositView.as_view(), name="deposit"),
    path("bonuses", BonusesListView.as_view(), name="bonuses-list"),
    
    # Level endpoints
    path("levels/current", CurrentLevelView.as_view(), name="current-level"),
    path("levels", LevelsListView.as_view(), name="levels-list"),
]

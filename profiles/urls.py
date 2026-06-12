from django.urls import path
from . import views
from .swipe_views import SwipeFeedView, SwipeActionView, MatchListView, ProfileBatchView, MeView

urlpatterns = [
    path('', views.BrowseView.as_view(), name='browse'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('edit/', views.ProfileUpdateView.as_view(), name='edit'),
    path('delete/', views.ProfileDeleteView.as_view(), name='delete'),
    path('matches/', views.MyMatchesView.as_view(), name='matches'),
    # Swipe API
    path('api/swipe/next/', SwipeFeedView.as_view(), name='swipe_feed'),
    path('api/swipe/action/', SwipeActionView.as_view(), name='swipe_action'),
    path('api/swipe/batch/', ProfileBatchView.as_view(), name='swipe_batch'),
    path('api/me/', MeView.as_view(), name='api_me'),
    path('api/matches/', MatchListView.as_view(), name='match_list'),
    path('swipe/', views.SwipePageView.as_view(), name='swipe_page'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProfileListView.as_view(), name='profile_list'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('delete/', views.ProfileDeleteView.as_view(), name='profile_delete'),
]

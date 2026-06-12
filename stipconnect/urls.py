from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView
from profiles.views import (
    ConsentSubmitView,
    CloudflareLogoutView,
    AdminPendingProfilesView,
    AdminApproveView,
    AdminRejectView,
    AdminToggleBetaView,
    AdminFeedbackListView,
    FeedbackFormView,
    BetaWaitlistView,
    BrowseProfilesView,
    MyMatchesView,
    WarteschlangeView,
)

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('browse')
    return redirect('home')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Cloudflare Access full logout (Django session + CF Access cookie)
    path('accounts/logout/', CloudflareLogoutView.as_view(), name='logout'),
    # Django-Standard-Login ENTFERNT — Auth läuft ausschließlich über Cloudflare Access
    path('profiles/', include('profiles.urls')),
    path('consent/', TemplateView.as_view(template_name='consent.html'), name='consent'),
    path('consent/submit/', ConsentSubmitView.as_view(), name='consent_submit'),
    path('datenschutz/', TemplateView.as_view(template_name='datenschutz.html'), name='datenschutz'),
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    path('mockup/', TemplateView.as_view(template_name='mockup.html'), name='mockup'),
    path('app/', home_redirect, name='app'),
    path('admin-dashboard/', AdminPendingProfilesView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/approve/<int:pk>/', AdminApproveView.as_view(), name='admin_approve'),
    path('admin-dashboard/reject/<int:pk>/', AdminRejectView.as_view(), name='admin_reject'),
    path('admin-dashboard/toggle-beta/<int:pk>/', AdminToggleBetaView.as_view(), name='admin_toggle_beta'),
    path('admin-feedback/', AdminFeedbackListView.as_view(), name='admin_feedback'),
    path('feedback/', FeedbackFormView.as_view(), name='feedback_form'),
    path('beta-waitlist/', BetaWaitlistView.as_view(), name='beta_waitlist'),
    path('warteschlange/', WarteschlangeView.as_view(), name='warteschlange'),
    # Simple Browse View (Task 3.1)
    path('browse/', BrowseProfilesView.as_view(), name='browse'),
    path('my-matches/', MyMatchesView.as_view(), name='my_matches'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

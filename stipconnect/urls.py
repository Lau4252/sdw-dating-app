from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView
from profiles.views import ConsentSubmitView

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('profile_list')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profiles/', include('profiles.urls')),
    path('consent/', TemplateView.as_view(template_name='consent.html'), name='consent'),
    path('consent/submit/', ConsentSubmitView.as_view(), name='consent_submit'),
    path('datenschutz/', TemplateView.as_view(template_name='datenschutz.html'), name='datenschutz'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home_redirect, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

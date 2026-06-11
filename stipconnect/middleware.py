import os
import logging
from django.contrib.auth import login, get_user_model
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)
User = get_user_model()

class CloudflareAccessMiddleware:
    """Authenticate users via Cloudflare Access headers.
    
    In production: reads CF-Access-Authenticated-User-Email from Cloudflare.
    In DEBUG mode: falls back to DEV_AUTH_EMAIL from settings.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        email = None
        if os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true':
            email = os.environ.get('DEV_AUTH_EMAIL')
        else:
            email = request.META.get('HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL')

        if email:
            user, created = User.objects.get_or_create(
                username=email,
                defaults={'email': email, 'first_name': '', 'last_name': ''}
            )
            if created:
                user.set_unusable_password()
                user.save()
                logger.info(f"Created new user from Cloudflare Access: {email}")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        elif not request.user.is_authenticated and not request.path.startswith('/admin/'):
            if os.environ.get('DJANGO_DEBUG', 'False').lower() != 'true':
                return HttpResponseForbidden(
                    "Zugriff nur über Cloudflare Access möglich. "
                    "Bitte melde dich über den Stipendiaten-Login an."
                )

        return self.get_response(request)

import os
import logging
from django.conf import settings
from django.contrib.auth import login, get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class CloudflareAccessMiddleware:
    """Authenticate users via Cloudflare Access headers.

    In production (behind Cloudflare Access): reads CF-Access-Authenticated-User-Email
    and auto-creates/logs in the Django user. No 403 here — Cloudflare Access handles
    the auth wall externally. Users without a valid Access session never reach this app.

    In DEBUG mode: reads the header first, then falls back to DEV_AUTH_EMAIL.

    Auto-creates both User and Profile to avoid race-conditions with post_save signals.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        email = request.META.get('HTTP_CF_ACCESS_AUTHENTICATED_USER_EMAIL')
        if not email and settings.DEBUG:
            email = os.environ.get('DEV_AUTH_EMAIL')

        if email:
            user, created = User.objects.get_or_create(
                username=email,
                defaults={'email': email, 'first_name': '', 'last_name': ''}
            )
            if created:
                user.set_unusable_password()
                user.save()
                logger.info(f"Created new user from Cloudflare Access: {email}")

            # Ensure Profile exists (explicit, independent of post_save signal)
            from profiles.models import Profile
            Profile.objects.get_or_create(user=user)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return self.get_response(request)

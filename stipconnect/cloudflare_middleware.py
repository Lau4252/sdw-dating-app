import logging
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils.deprecation import MiddlewareMixin
from profiles.models import Profile

logger = logging.getLogger(__name__)

class CloudflareAccessMiddleware(MiddlewareMixin):
    """
    Reads CF-Access-User-Email header from Cloudflare Access
    Auto-creates User and Profile if not exists
    """
    
    def process_request(self, request):
        # Get email from Cloudflare Access header
        email = request.META.get('HTTP_CF_ACCESS_USER_EMAIL')
        
        if not email:
            # Try alternative header names
            email = request.META.get('HTTP_CF_ACCESS_JWT_ASSERTION')
            if email:
                # JWT token - we'd need to decode it, skip for now
                email = None
        
        if email and request.user.is_anonymous:
            try:
                # Get or create user
                username = email.split('@')[0][:30]
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'first_name': '',
                        'last_name': '',
                    }
                )
                
                if created:
                    logger.info(f"Auto-created user: {email}")
                    # Profile is auto-created via signal
                    # Set user as staff for admin access if needed
                
                # Log user in
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                
            except Exception as e:
                logger.error(f"Cloudflare auth error: {e}")
        
        return None

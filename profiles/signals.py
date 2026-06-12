from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Erstellt automatisch ein leeres Profile mit Auto-Approval (kein Pending)."""
    if created:
        Profile.objects.get_or_create(user=instance, defaults={
            'pending': False,   # Auto-Approval: Sofort freigeschaltet
            'visible': False,  # Sichtbar erst nach Consent
        })


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Speichert das zugehörige Profile wenn der User gespeichert wird."""
    if hasattr(instance, 'profile'):
        instance.profile.save()

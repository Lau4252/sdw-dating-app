from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, verbose_name="Über mich")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    study_program = models.CharField(max_length=100, blank=True, verbose_name="Studiengang")
    city = models.CharField(max_length=100, blank=True, verbose_name="Stadt")
    photo = models.ImageField(upload_to='photos/%Y/%m/', blank=True, null=True, verbose_name="Foto")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Geburtstag")
    interests = models.CharField(max_length=255, blank=True, verbose_name="Interessen")
    consent_given = models.BooleanField(default=False, verbose_name="Einwilligung erteilt")
    consent_date = models.DateTimeField(blank=True, null=True, verbose_name="Einwilligungsdatum")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('profile_detail', kwargs={'pk': self.pk})

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

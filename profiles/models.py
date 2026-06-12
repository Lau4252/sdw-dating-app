from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Mann'),
        ('F', 'Frau'),
        ('D', 'Divers'),
    ]
    
    SEEKING_CHOICES = [
        ('M', 'Männer'),
        ('F', 'Frauen'),
        ('A', 'Alle'),
    ]
    
    LOOKING_FOR_CHOICES = [
        ('serious', '💛 Etwas Ernstes'),
        ('open', '🥂 Offen — Freunde & mehr'),
        ('casual', '✨ Mal schauen'),
    ]
    
    TRINKEN_CHOICES = [
        ('nie', 'Nie'),
        ('selten', 'Selten'),
        ('gesellig', 'Gesellig am Wochenende'),
        ('regelmaessig', 'Regelmäßig'),
    ]
    
    RAUCHEN_CHOICES = [
        ('nie', 'Nichtraucher(in)'),
        ('gelegentlich', 'Gelegentlich'),
        ('regelmaessig', 'Regelmäßig'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Sichtbarkeit & Status
    visible = models.BooleanField(default=False, verbose_name="Sichtbar")
    pending = models.BooleanField(default=True, verbose_name="Freigabe ausstehend")
    
    # Beta-Tester Flag (Invite-Only Phase)
    is_beta_tester = models.BooleanField(default=False, verbose_name="Beta-Tester")
    
    # Basis-Info
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Geschlecht")
    seeking = models.CharField(max_length=1, choices=SEEKING_CHOICES, blank=True, verbose_name="Suche nach")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Geburtstag")
    
    # Studium & Region
    studienfach = models.CharField(max_length=100, blank=True, verbose_name="Studienfach")
    hochschule = models.CharField(max_length=100, blank=True, verbose_name="Hochschule")
    regionen = models.JSONField(default=list, blank=True, verbose_name="Regionen")
    sprachen = models.CharField(max_length=100, blank=True, verbose_name="Sprachen")
    
    # Profil-Inhalt
    quote = models.CharField(max_length=200, blank=True, verbose_name="Mein Spruch")
    about = models.TextField(blank=True, verbose_name="Über mich")
    looking_for = models.CharField(max_length=20, choices=LOOKING_FOR_CHOICES, blank=True, verbose_name="Suche nach")
    
    # Lifestyle
    trinken = models.CharField(max_length=20, choices=TRINKEN_CHOICES, blank=True, verbose_name="Trinken")
    rauchen = models.CharField(max_length=20, choices=RAUCHEN_CHOICES, blank=True, verbose_name="Rauchen")
    
    # Interessen (JSON-Array)
    interests = models.JSONField(default=list, blank=True, verbose_name="Interessen")
    
    # Fotos (JSON-Array mit URLs — deprecated, nutze photo ImageField stattdessen)
    photos = models.JSONField(default=list, blank=True, verbose_name="Fotos")

    # Profilfoto (echter Datei-Upload)
    photo = models.ImageField(upload_to='photos/%Y/%m/', blank=True, null=True, verbose_name="Profilfoto")
    
    # Kontakt
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    
    # Einwilligung
    consent_given = models.BooleanField(default=False, verbose_name="Einwilligung erteilt")
    consent_date = models.DateTimeField(blank=True, null=True, verbose_name="Einwilligungsdatum")
    
    # Prompts (Frage-Antwort-Paare)
    prompts = models.JSONField(default=list, blank=True, verbose_name="Prompts")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}"

    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('profile_detail', kwargs={'pk': self.pk})

class Swipe(models.Model):
    """Speichert Like/Pass-Entscheidungen zwischen Usern."""
    DECISION_CHOICES = [
        ('like', 'Like'),
        ('pass', 'Pass'),
    ]
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swipes_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swipes_received')
    decision = models.CharField(max_length=4, choices=DECISION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']
        ordering = ['-created_at']
        verbose_name = "Swipe"
        verbose_name_plural = "Swipes"

    def __str__(self):
        return f"{self.from_user} → {self.to_user}: {self.decision}"

    @classmethod
    def is_match(cls, user1, user2):
        """Prüft, ob beide User sich gegenseitig geliket haben."""
        return (cls.objects.filter(from_user=user1, to_user=user2, decision='like').exists()
                and cls.objects.filter(from_user=user2, to_user=user1, decision='like').exists())

    @classmethod
    def get_matches(cls, user):
        """Gibt alle gegenseitigen Likes (Matches) eines Users zurück."""
        liked_ids = cls.objects.filter(from_user=user, decision='like').values_list('to_user_id', flat=True)
        mutual_ids = cls.objects.filter(from_user_id__in=liked_ids, to_user=user, decision='like').values_list('from_user_id', flat=True)
        return User.objects.filter(id__in=mutual_ids)

class MatchView(models.Model):
    """Speichert, wann ein User einen Match gesehen hat."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_views')
    other_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_viewed_by')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'other_user']
        verbose_name = "Match View"
        verbose_name_plural = "Match Views"


class FeedbackEntry(models.Model):
    """Beta-Feedback, Bug-Reports und Feature-Wünsche."""
    FEEDBACK_TYPES = [
        ('bug', '🐛 Bug-Report'),
        ('feature', '💡 Feature-Wunsch'),
        ('feedback', '📝 Allgemeines Feedback'),
        ('other', '🧩 Sonstiges'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', verbose_name="User")
    typ = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='feedback', verbose_name="Typ")
    text = models.TextField(verbose_name="Nachricht")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return f"{self.typ} von {self.user.email} ({self.created_at:%d.%m.%Y %H:%M})"


class Message(models.Model):
    """Chat-Nachricht zwischen zwei gematchten Usern."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_received')
    text = models.TextField(verbose_name="Nachricht")
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True, verbose_name="Gelesen am")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Nachricht"
        verbose_name_plural = "Nachrichten"
        indexes = [
            models.Index(fields=['sender', 'recipient', '-created_at']),
            models.Index(fields=['recipient', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.text[:50]}"

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_read(self):
        from django.utils import timezone
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

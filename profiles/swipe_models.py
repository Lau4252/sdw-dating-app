from django.db import models
from django.contrib.auth.models import User

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
    
    def __str__(self):
        return f"{self.from_user} → {self.to_user}: {self.decision}"
    
    @classmethod
    def is_match(cls, user1, user2):
        """Prüft, ob beide User sich gegenseitig geliket haben."""
        return cls.objects.filter(
            from_user=user1, to_user=user2, decision='like'
        ).exists() and cls.objects.filter(
            from_user=user2, to_user=user1, decision='like'
        ).exists()
    
    @classmethod
    def get_matches(cls, user):
        """Gibt alle gegenseitigen Likes (Matches) eines Users zurück."""
        liked_ids = cls.objects.filter(
            from_user=user, decision='like'
        ).values_list('to_user_id', flat=True)
        
        mutual_ids = cls.objects.filter(
            from_user_id__in=liked_ids,
            to_user=user,
            decision='like'
        ).values_list('from_user_id', flat=True)
        
        return User.objects.filter(id__in=mutual_ids)

class MatchView(models.Model):
    """Speichert, wann ein User einen Match gesehen hat."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_views')
    other_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_viewed_by')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'other_user']

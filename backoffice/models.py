from django.db import models

# Create your models here.
# ads/models.py
from django.db import models
from django.utils import timezone

class Ad(models.Model):
    POSITION_CHOICES = [
        ("header", "Haut de page"),
        ("sidebar", "Barre latérale"),
        ("footer", "Pied de page"),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="ads/")
    link = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default="sidebar")
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        now = timezone.now()
        return self.active and (self.start_date <= now) and (not self.end_date or now <= self.end_date)

    def __str__(self):
        return self.title

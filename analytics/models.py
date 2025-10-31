from django.db import models
from django.utils import timezone

class Visit(models.Model):
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.path} - {self.ip_address}"

class DailyStats(models.Model):
    date = models.DateField(unique=True)
    total_visits = models.IntegerField(default=0)
    unique_ips = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.total_visits} visits"

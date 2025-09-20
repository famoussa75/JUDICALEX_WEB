from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from start.models import Juridictions
from django.utils.timezone import now
from django.dispatch import receiver
from django.contrib.auth.models import User






# Create your models here.
class Account(AbstractUser):
    # Ajoutez ici d'autres champs personnalisés pour votre modèle Account si nécessaire
    juridiction = models.ForeignKey(Juridictions,null=True, blank=True, on_delete=models.CASCADE)
    adresse = models.TextField(null=True, blank=True, verbose_name=_('Adresse'))
    profession = models.TextField(null=True, blank=True, verbose_name=_('Profession'))
    tel1 = models.TextField(null=True, blank=True, verbose_name=_('Telephone 1'))
    tel2 = models.TextField(null=True, blank=True, verbose_name=_('Telephone 2'))
    nationnalite = models.TextField(null=True, blank=True, verbose_name=_('Nationnalité'))
    photo = models.FileField(upload_to='account/photos/', null=True, blank=True, verbose_name=_('photos'))




class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
    )

    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    message = models.TextField()
    objet_cible = models.IntegerField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)  # Lien associé à la notification
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.type.capitalize()} - {self.message[:20]}"
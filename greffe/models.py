import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

from start.models import Juridictions



# Account.
class Account(models.Model):
    # Ajoutez ici d'autres champs personnalisés pour votre modèle Account si nécessaire
    juridiction = models.ForeignKey(Juridictions,null=True, blank=True, on_delete=models.CASCADE, related_name=_('greffe_juridiction'))
    username = models.TextField(null=True, blank=True, verbose_name=_('Nom utilisateur'))
    first_name = models.TextField(null=True, blank=True, verbose_name=_('Prenom'))
    last_name = models.TextField(null=True, blank=True, verbose_name=_('Nom'))
    adresse = models.TextField(null=True, blank=True, verbose_name=_('Adresse utilisateur'))
    poste = models.TextField(null=True, blank=True, verbose_name=_('Poste'))
    tel1 = models.TextField(null=True, blank=True, verbose_name=_('Telephone 1'))
    tel2 = models.TextField(null=True, blank=True, verbose_name=_('Telephone 2'))
    nationnalite = models.TextField(null=True, blank=True, verbose_name=_('Nationnalité'))
    photo = models.FileField(upload_to='account/photos/', null=True, blank=True, verbose_name=_('photo'))

    def __str__(self):
        """
        Retourne le prénom et le nom capitalisés comme représentation textuelle de l'utilisateur.
        Si l'un des deux est manquant, retourne uniquement l'attribut disponible.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
        elif self.first_name:
            return self.first_name.capitalize()
        elif self.last_name:
            return self.last_name.capitalize()
        else:
            return self.username  # Par défaut, retourne le nom d'utilisateur
        

class Signature(models.Model):
    chef_greffe = models.OneToOneField(
        'Account',
        on_delete=models.CASCADE,
        related_name='signature',
        verbose_name=_('Chef de Greffe')
    )
    image = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        verbose_name=_('Image de la Signature')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Date de création'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Date de mise à jour'))

    def __str__(self):
        return f"Signature de {self.chef_greffe.username}"

from django.db import models

class ContactPro(models.Model):
    CIVILITE_CHOICES = [
        ('M.', 'Monsieur'),
        ('Mme', 'Madame'),
        ('Me', 'Maître'),
    ]

    FONCTION = [
        ('avocat', 'Avocat(e)'),
        ('notaire', 'Notaire'),
        ('huissier', 'Huissier de justice'),
        ('expert', 'Expert judiciaire'),
        ('autre', 'Autre'),
    ]

    civilite = models.TextField(choices=CIVILITE_CHOICES, default='M.')
    nom = models.TextField()
    prenom = models.TextField(blank=True)
    fonction = models.TextField(choices=FONCTION, default='avocat')
    telephone = models.CharField(max_length=30)
    email = models.EmailField()
    adresse = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact professionnel"
        verbose_name_plural = "Contacts professionnels"
        ordering = ['nom']

    def __str__(self):
        return f"{self.civilite} {self.nom} ({self.fonction})"


class Lien(models.Model):
    titre = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.titre

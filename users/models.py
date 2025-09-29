from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from start.models import Juridictions
from django.utils.timezone import now
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
import os
import unicodedata
from django.utils.text import slugify

def contribution_upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    safe_name = slugify(unicodedata.normalize("NFKD", name))
    return f"contribution_ids/{safe_name}{ext}"

# … (import de Juridictions)

class ProfessionChoices(models.TextChoices):
    AVOCAT              = "AVOCAT", _("Avocat")
    MAGISTRAT           = "MAGISTRAT", _("Magistrat")
    GREFFIER            = "GREFFIER", _("Greffier")
    HUISSIER            = "HUISSIER", _("Huissier de justice")
    NOTAIRE             = "NOTAIRE", _("Notaire")
    JURISTE_ENTREPRISE  = "JURISTE_ENT", _("Juriste d'entreprise")
    CONSEILLER_JUR      = "CONSEILLER_JUR", _("Conseiller juridique")
    ETUDIANT_DROIT      = "ETUDIANT_DRT", _("Étudiant en droit")
    ENSEIGNANT_DROIT    = "ENSEIGNANT_DRT", _("Enseignant-chercheur en droit")
    SECRETAIRE_JUR      = "SECRETAIRE_JUR", _("Secrétaire juridique")
    ASSISTANT_JUR       = "ASSISTANT_JUR", _("Assistant juridique")
    MEDIATEUR           = "MEDIATEUR", _("Médiateur")
    ARBITRE             = "ARBITRE", _("Arbitre")
    POLICE_GENDARMERIE  = "POLICE_GNDR", _("Police / Gendarmerie")
    ADMIN_CIVIL         = "ADMIN_CIVIL", _("Administrateur civil")
    INSPECTEUR_TRAVAIL  = "INSP_TRAVAIL", _("Inspecteur du travail")
    ETAT_CIVIL          = "ETAT_CIVIL", _("Officier de l'état civil")
    FISCALISTE          = "FISCALISTE", _("Fiscaliste")
    COMPTABLE           = "COMPTABLE", _("Comptable")
    EXPERT_COMPTABLE    = "EXPERT_COMPT", _("Expert-comptable")
    CONSULTANT          = "CONSULTANT", _("Consultant")
    ENTREPRENEUR        = "ENTREPRENEUR", _("Entrepreneur / Dirigeant")
    JOURNALISTE         = "JOURNALISTE", _("Journaliste (presse juridique)")
    TRADUCTEUR_ASSER    = "TRAD_ASSE", _("Traducteur assermenté")
    LEGALTECH_INGE      = "LEGALTECH", _("Ingénieur / Informaticien (LegalTech)")
    AUTRE               = "AUTRE", _("Autre")

class Account(AbstractUser):
    juridiction = models.ForeignKey(Juridictions, null=True, blank=True, on_delete=models.CASCADE)
    adresse = models.TextField(null=True, blank=True, verbose_name=_('Adresse'))
    profession = models.CharField(
        max_length=32,
        choices=ProfessionChoices.choices,
        null=True, blank=True,
        verbose_name=_('Profession'),
    )
    tel1 = models.TextField(null=True, blank=True, verbose_name=_('Téléphone 1'))
    tel2 = models.TextField(null=True, blank=True, verbose_name=_('Téléphone 2'))
    nationnalite = models.TextField(null=True, blank=True, verbose_name=_('Nationalité'))
    photo = models.FileField(upload_to='users/photos/', null=True, blank=True, verbose_name=_('Photo'))

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            group, _ = Group.objects.get_or_create(name="Visiteur")
            self.groups.add(group)




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
    


class ContributionRequest(models.Model):

    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Approuvée"),
        ("rejected", "Rejetée"),
    ]
    
    demandeur = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandeur')
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    motivation = models.TextField()
    piece_identite = models.FileField(
        upload_to=contribution_upload_to,
        verbose_name="Pièce d'identité (PDF ou image)"
    )
    created_at = models.DateTimeField(default=now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Demande de {self.user.username} ({self.nom})"
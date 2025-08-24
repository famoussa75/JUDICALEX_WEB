from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from users.models import Account,Notification
from role.models import Decisions, SuivreAffaire

@receiver(post_save, sender=Account)
def notify_new_user(sender, instance, created, **kwargs):
    if created:
        print(f"Signal déclenché pour {instance.first_name}")
        Notification.objects.create(
            recipient=instance,
            type='success',
            message=f"Bienvenue, {instance.first_name} !",
            url='profile/'
        )


@receiver(post_save, sender=Decisions)
def notify_new_decision(sender, instance, created, **kwargs):
    if created:
        print(f"Signal déclenché pour {instance.decision}")
        suivreAffaire = SuivreAffaire.objects.filter(affaire=instance.affaire)
        for s in suivreAffaire:
            Notification.objects.create(
                recipient=s.account,
                type='info',
                objet_cible=s.affaire_id,
                message=f"Vous venez d'obtenir une décision sur l'affaire N°{s.affaire_id} - {s.juridiction} !",
                url=f"/role/affaires/details/{instance.affaire.idAffaire}"
            )

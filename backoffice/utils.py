from django.contrib.auth import get_user_model
from users.models import Notification

User = get_user_model()

def create_notification(recipient, sender, type, message, objet_cible=None, url=None):
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=type,
        message=message,
        objet_cible=objet_cible,
        url=url
    )

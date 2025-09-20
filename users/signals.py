from allauth.socialaccount.signals import social_account_added
from allauth.account.models import EmailAddress
from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings


@receiver(social_account_added)
def activate_google_user(request, sociallogin, **kwargs):
    user = sociallogin.user
    if sociallogin.account.provider == 'google':
        user.is_active = True  # Assurer qu’il est actif
        user.save()


@receiver(email_confirmed)
def send_welcome_email(request, email_address, **kwargs):
    """
    Envoie un email de bienvenue après confirmation de l'adresse email.
    """
    user = email_address.user
    context = {
        'user': user,
        'site_name': 'Ton Application',
        'current_year': timezone.now().year,
        'dashboard_url': request.build_absolute_uri('/dashboard/')  # adapter si autre URL
    }

    subject = f"Bienvenue sur {context['site_name']} !"
    text_content = render_to_string('account/email/welcome_email.txt', context)
    html_content = render_to_string('account/email/welcome_email.html', context)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

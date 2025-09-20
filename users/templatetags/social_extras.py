from django import template
from allauth.socialaccount.models import SocialAccount

register = template.Library()

@register.filter
def social_avatar(user):
    """
    Retourne l'URL de l'avatar social si l'utilisateur a connecté un compte social.
    """
    if not user:
        return ''
    account = SocialAccount.objects.filter(user=user).first()
    if account:
        return account.get_avatar_url()
    return ''

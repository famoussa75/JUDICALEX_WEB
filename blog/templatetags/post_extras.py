from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def within_hours(dt, hours=24):
    """
    Retourne True si `dt` est dans les dernières `hours` heures.
    """
    if not dt:
        return False
    try:
        now = timezone.now()
        return (now - dt) < timedelta(hours=int(hours))
    except Exception:
        return False

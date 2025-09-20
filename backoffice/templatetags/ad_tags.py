# ads/templatetags/ad_tags.py
from django import template
from ..models import Ad
from django.utils import timezone

register = template.Library()

@register.inclusion_tag("ads/ad_display.html")
def show_ads(position):
    now = timezone.now()
    ads = Ad.objects.filter(
        position=position,
        active=True,
        start_date__lte=now
    ).filter(end_date__isnull=True) | Ad.objects.filter(
        position=position,
        active=True,
        start_date__lte=now,
        end_date__gte=now
    )
    return {"ads": ads}

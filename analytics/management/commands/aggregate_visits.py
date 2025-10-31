from django.core.management.base import BaseCommand
from analytics.models import Visit, DailyStats
from django.db.models import Count
from django.utils import timezone

class Command(BaseCommand):
    help = "Agrège les visites du jour dans DailyStats"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        visits_today = Visit.objects.filter(created_at__date=today)

        total = visits_today.count()
        unique_ips = visits_today.values('ip_address').distinct().count()

        stats, created = DailyStats.objects.get_or_create(date=today)
        stats.total_visits = total
        stats.unique_ips = unique_ips
        stats.save()

        self.stdout.write(self.style.SUCCESS(f"Agrégation terminée pour {today}: {total} visites"))

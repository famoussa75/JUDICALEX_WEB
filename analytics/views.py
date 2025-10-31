from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from analytics.models import DailyStats

@csrf_exempt
def stats_data(request):
    data = DailyStats.objects.order_by('date').values('date', 'total_visits', 'unique_ips')
    return JsonResponse(list(data), safe=False)

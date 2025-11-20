from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from analytics.models import DailyStats

@csrf_exempt
def stats_data(request):
    data = DailyStats.objects.order_by('-date')[:7].values('date', 'total_visits', 'unique_ips')
    data = data[::-1]
    return JsonResponse(list(data), safe=False)

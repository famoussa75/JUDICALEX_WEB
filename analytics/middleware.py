from .models import Visit
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
import threading

class AnalyticsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # On ne trace que les pages GET normales
        if (
            request.method == 'GET'
            and not request.path.startswith('/admin')
            and not request.path.startswith('/static')
        ):
            # On exécute dans un thread pour ne pas ralentir la réponse
            def save_visit():
                Visit.objects.create(
                    path=request.path,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                    referer=request.META.get('HTTP_REFERER', '')
                )
            threading.Thread(target=save_visit).start()
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

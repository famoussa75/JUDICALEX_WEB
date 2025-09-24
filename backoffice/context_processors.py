# backoffice/context_processors.py
from users.models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        # toutes les notifications, triées par date décroissante
        notifications = request.user.notifications.all().order_by('-timestamp')
        # notifications non lues
        unread_notifications = notifications.filter(is_read=False)
        unread_count = unread_notifications.count()
    else:
        notifications = []
        unread_notifications = []
        unread_count = 0

    return {
        'notifications': notifications,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
    }

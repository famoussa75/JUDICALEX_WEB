
from django.contrib import admin
from django.urls import path, include
from start import views
from django.conf.urls.static import static
from django.conf import settings
from role.views import NePasSuivreAffaire,suivreAffaire
from .views import DeleteNotificationsAPIView, MarkNotificationAsReadAPIView, allNotificationAPIView, api_sign_in, api_sign_up, api_sign_out,api_delete_account,api_update_account, detail_affaire_api,get_user,mes_affaires_suivies_api, PostDetailAPIView, PostListAPIView, CommentCreateAPIView, RolesListAPI, ne_pas_suivre_affaire_api, role_detail_api, suivre_affaire_api, send_contact_email, about_us,notificationAPIView, ges_message


urlpatterns = [
    path('', views.index, name='home'),
    path('accounts/', include('allauth.urls')),
    path('gestion-messages/', ges_message, name='ges_message'),
    path('gestion-messages/<int:pk>/<str:action>/', ges_message, name='gestion_messages_edit'),

    path('divers/', include('divers.urls')),
    path('entreprise/', include('entreprise.urls')),
    path('emploi/', include('emploi.urls')),
    path('role/', include('role.urls')),
    path('magistrats/', include('magistrats.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
    path('suivre-affaire/', suivreAffaire, name='suivre-affaire'),
    path('ne-pas-suivre-affaire/', NePasSuivreAffaire, name='ne-pas-suivre-affaire'),
    path('blog/', include('blog.urls')),
    path('rccm/', include('rccm.urls')),

    #API REST FOR FLUTTER APP
    path('api/signin/', api_sign_in, name='api_sign_in'),
    path('api/signup/', api_sign_up, name='api_sign_up'),
    path('api/signout/', api_sign_out, name='api_sign_out'),
    path('api/account/update/<int:user_id>/', api_update_account, name='api_update_account'),
    path('api/account/delete/<int:user_id>/', api_delete_account, name='api_delete_account'),
    path('api/account/get-user/<int:user_id>/', get_user, name='get_user'),
    

    path('api/posts/', PostListAPIView.as_view(), name='post_list_api'),
    path('api/posts/<int:pk>/', PostDetailAPIView.as_view(), name='post_detail_api'),
    path('api/posts/<int:pk>/comment/', CommentCreateAPIView.as_view(), name='add_comment_api'),

    path('api/roles/', RolesListAPI.as_view(), name='roles-list'),
    path('api/role/<int:pk>/', role_detail_api, name='role-detail-api'),
    path('api/affaire/<int:idAffaire>/', detail_affaire_api, name='detail-affaire-api'),
    path('api/suivre-affaire/', suivre_affaire_api, name='suivre-affaire-api'),
    path('api/ne-pas-suivre-affaire/', ne_pas_suivre_affaire_api, name='ne-pas-suivre-affaire-api'),
    path('api/mes-affaires-suivies/', mes_affaires_suivies_api, name='mes_affaires_suivies_api'),

    path('send_email/', send_contact_email, name='send_email'),

    path('a_propos/', about_us, name='about_us'),

    path('api/notifications/', notificationAPIView, name='notification-list'),
    path('api/notifications/all/', allNotificationAPIView, name='notification-list-all'),
    path('api/notifications/<int:notification_id>/mark-as-read/', MarkNotificationAsReadAPIView.as_view(), name='mark-notification-as-read'),
    path('api/notifications/delete-all/', DeleteNotificationsAPIView.as_view(), name='delete-notifications'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


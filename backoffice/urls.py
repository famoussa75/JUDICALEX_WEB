from django.urls import path, include
from . import views
from . import views_users as uviews
from . import views_groups as gviews
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
     path('', views.login, name='backoffice.login'),


     # Admin URLs
     path("post/post_list/", views.post_list, name="post_list"),
     path("post/create/", views.post_create, name="post_create"),
     path("post/<slug:slug>/", views.post_detail, name="post_detail"),
     path("post/<slug:slug>/update/", views.post_update, name="post_update"),
     path("post/<slug:slug>/delete/", views.post_delete, name="post_delete"),
     path("post/<slug:slug>/publish/", views.post_publish, name="post_publish"),
     path("post/<slug:slug>/unpublish/", views.post_unpublish, name="post_unpublish"),
     path('notifications/', views.notifications_list, name='notifications_list'),
     path('notification/<int:pk>/read/', views.read_notification, name='read_notification'),
     path('notifications/mark_all_read/', views.mark_all_notifications_read, name='notifications_mark_all_read'),
     path('notifications/delete-all/', views.notifications_delete_all, name='notifications_delete_all'),



     path("demandes/", views.liste_demandes, name="liste_demandes"),
     path("demandes/<int:demande_id>/", views.details_demande, name="details_demande"),
     path("demandes/<int:demande_id>/approuver/", views.approuver_demande, name="approuver_demande"),
     path("demandes/<int:demande_id>/rejeter/", views.rejeter_demande, name="rejeter_demande"),

    # Users
    path("users/", uviews.user_list, name="user.list"),
    path("users/create/", uviews.user_create, name="user.create"),
    path("users/<int:pk>/edit/", uviews.user_update, name="user.edit"),
    path("users/<int:pk>/delete/", uviews.user_delete, name="user.delete"),

    # Groups
    path("groups/", gviews.group_list, name="groups.list"),
    path("groups/create/", gviews.group_create, name="groups.create"),
    path("groups/<int:pk>/edit/", gviews.group_update, name="groups.edit"),
    path("groups/<int:pk>/delete/", gviews.group_delete, name="groups.delete"),

    # Ads
    path("ads/", views.ad_list, name="ad_list"),
    path("create/", views.ad_create, name="ad_create"),
    path("<int:pk>/edit/", views.ad_edit, name="ad_edit"),
    path("<int:pk>/delete/", views.ad_delete, name="ad_delete"),
    path("<int:pk>/click/", views.ad_click, name="ad_click"),
    path('ad-impression/', views.ad_impression, name='ad_impression'),

    # Comments internal
    path("comment_internal/create/<slug:slug>/", views.comment_create, name="comment_create"),
    path("comment_internal/<int:comment_id>/<slug:slug>/delete/", views.comment_delete, name="comment_delete"),

     path("demandes/", views.liste_demandes, name="liste_demandes"),
     path("demandes/<int:demande_id>/", views.details_demande, name="details_demande"),
     path("demandes/<int:demande_id>/approuver/", views.approuver_demande, name="approuver_demande"),
     path("demandes/<int:demande_id>/rejeter/", views.rejeter_demande, name="rejeter_demande"),

      # 🔐 Déconnexion
    path("logout/", uviews.logout_view, name="user.logout"),

]

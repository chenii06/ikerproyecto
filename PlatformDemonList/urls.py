"""PlatformDemonList URLs module."""

# Django
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.urls import path, re_path, include, reverse_lazy
from django.views.static import serve

# Views
from PlatformDemonList import views
from apps.demonlist.views.views import custom_404_view

# Forms
from apps.users import forms

urlpatterns = [

    path('admin/', admin.site.urls),
    path('ads.txt', serve, {'document_root': settings.BASE_DIR, 'path': 'ads.txt'}),

    path("users/", include(("apps.users.urls", "users"), namespace="users")),
    path('accounts/', include('allauth.urls')),

    re_path(
        route=r'^reset_password/?$',
        view=views.CustomPasswordResetView.as_view(),
        name='reset_password'
    ),
    re_path(
        route=r'^reset_password_sent/?$',
        view=views.CustomPasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    re_path(
        route=r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/?$',
        view=views.CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    re_path(
        route=r'^reset_password_complete/?$',
        view=views.CustomPasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),

    re_path(
        route=r'^reset_email/?$',
        view=views.CustomEmailResetView.as_view(),
        name='reset_email'
    ),
    re_path(
        route=r'^reset_email_sent/?$',
        view=views.CustomEmailResetDoneView.as_view(),
        name='email_reset_done'
    ),
    re_path(
        route=r'^reset_email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/?$',
        view=views.CustomEmailResetConfirmView.as_view(),
        name='email_reset_confirm'
    ),
    re_path(
        route=r'^reset_email_complete/?$',
        view=views.CustomEmailResetCompleteView.as_view(),
        name='email_reset_complete'
    ),
    re_path(
        route=r'^terms/?$',
        view=views.TermsView.as_view(),
        name='terms'
    ),

    re_path(
        route=r'^guidelines/?$',
        view=views.GuidelinesView.as_view(),
        name='guidelines'
    ),

    re_path(
        route=r'^credits/?$',
        view=views.CreditsView.as_view(),
        name='credits'
    ),
    re_path(
        route=r'^settings/?$',
        view=views.SettingsView.as_view(),
        name='settings'
    ),

    path('', include(('apps.demonlist.urls', 'demonlist'), namespace='demonlist')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = custom_404_view

# Django
from django.urls import path, re_path

# View
from apps.users.views import views, views_discord


urlpatterns = [

    # Management
    re_path(
        route=r'^oauth2/login/?$',
        view=views_discord.discord_login,
        name='discord_login'
    ),
    re_path(
        route=r'^oauth2/login/redirect/?$',
        view=views_discord.DiscordLoginRedirectView.as_view(),
        name='discord_login_redirect'
    ),
    re_path(
        route=r'^update_account/?$',
        view=views_discord.UpdateAccount.as_view(),
        name='update_account'
    ),
    re_path(
        route=r'^demo_recaptcha/?$',
        view=views.demo_recaptcha,
        name='demo_recaptcha'
    ),
    re_path(
        route=r'^read_notifications/?$',
        view=views.ReadNotifications.as_view(),
        name='read_notifications'
    ),
    re_path(
        route=r'^login/?$',
        view=views.LoginView.as_view(),
        name='login'
    ),
    re_path(
        route=r'^logout/?$',
        view=views.LogoutView.as_view(),
        name='logout'
    ),
    re_path(
        route=r'^signup/?$',
        view=views.SignupView.as_view(),
        name='signup'
    ),
    re_path(
        route=r'^me/?$',
        view=views.UpdateProfileView.as_view(),
        name='update'
    ),
    re_path(
        route=r'^me/teams/?$',
        view=views.TeamsView.as_view(),
        name='teams'
    ),
    re_path(
        route=r'^me/records_status/?$',
        view=views.RecordsStatusView.as_view(),
        name='records_status'
    ),

    # Rutas con expresión regular

    re_path(
        route=r'^(?P<user>\d+)/?$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),
]
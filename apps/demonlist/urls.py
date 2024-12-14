"""DemonList URLs."""

# Django
from django.urls import path, re_path

# Views
from apps.demonlist.views import views, views_api
from PlatformDemonList import views as global_views

urlpatterns = [

    path(
        route=r'',
        view=views.HomeView.as_view(),
        name='home'
    ),
    re_path(
        route=r'^vote_stars/(?P<pk>\d+)/?$',
        view=views.VoteStarsView.as_view(),
        name='vote_stars'
    ),
    re_path(
        route=r'^roulette/(?P<pk>\d+)/?$',
        view=views.RouletteView.as_view(),
        name='roulette'
    ),
    re_path(
        route=r'^submit_record/?$',
        view=views.SubmitRecordView.as_view(),
        name='submit_record'
    ),
    re_path(
        route=r'^stats_viewer/?$',
        view=views.StatsViewerView.as_view(),
        name='stats_viewer'
    ),
    re_path(
        route=r'^check_records/?$',
        view=views.CheckRecordsView.as_view(),
        name='check_records'
    ),
    re_path(
        route=r'^check_profiles/?$',
        view=views.CheckProfilesView.as_view(),
        name='check_profiles'
    ),
    re_path(
        route=r'^add_edit_demon/?$',
        view=views.AddEditDemonView.as_view(),
        name='add_edit_demon'
    ),
    re_path(
        route=r'^add_edit_profile/?$',
        view=views.AddEditProfileView.as_view(),
        name='add_edit_profile'
    ),
    re_path(
        route=r'^roulette/?$',
        view=views.CreateRouletteView.as_view(),
        name='create_roulette'
    ),
    re_path(
        route=r'^roulette_menu/?$',
        view=views.RouletteMenuView.as_view(),
        name='roulette_menu'
    ),
    re_path(
        route=r'^diary_role/?$',
        view=views.DiaryRole.as_view(),
        name='diary_role'
    ),
    re_path(
        route=r'^change_language/?$',
        view=views.change_language,
        name='change_language'
    ),

    # API

    re_path(
        route=r'^api/level/?$',
        view=views_api.DemonApi.as_view(),
        name='demon_api'
    ),

    # Rutas con expresión regular

    re_path(
        route=r'^id/(?P<level_id>\d+)/?$',
        view=views.DemonDetailView.as_view(),
        name='level_id_detail'
    ),
    re_path(
        route=r'^(?P<category>\w+)/(?P<position>\d+)/?$',
        view=views.DemonDetailView.as_view(),
        name='detail'
    ),
    re_path(
        route=r'^(?P<category>\w+)/level_packs/?$',
        view=views.LevelPacksView.as_view(),
        name='level_packs'
    ),
    re_path(
        route=r'^(?P<mode>\w+)/(?P<category>\w+)/?$',
        view=views.DemonListView.as_view(),
        name='list'
    ),
    re_path(
        route=r'^(?P<mode>\w+)/(?P<category>\w+)/legacy/?$',
        view=views.DemonListView.as_view(),
        name='list_legacy'
    ),
    re_path(
        route=r'^(?P<mode>\w+)/(?P<category>\w+)/level_packs/?$',
        view=views.LevelPacksView.as_view(),
        name='level_packs'
    ),
    re_path(
        route=r'^(?P<mode>\w+)/(?P<category>\w+)/(?P<position>\d+)/?$',
        view=views.DemonDetailView.as_view(),
        name='detail'
    ),
    re_path(
        route=r'^(?P<value>[^/]+)/?$',
        view=views.CategoryOrUsernameView.as_view(),
        name='category_or_username'
    ),
]
"""DemonList models."""

# Django
from django.contrib import admin
from django.contrib.auth.models import Group

# Models
from apps.demonlist.models import Demon, Record, Changelog, Roulette, RouletteDemon, LevelPack
from django.contrib.auth.models import User

class ProfileModFilter(admin.SimpleListFilter):
    title = 'Profile Mod'
    parameter_name = 'profile_mod'

    def lookups(self, request, model_admin):
        list_helper_group = Group.objects.get(name='Platformer Rated List Helper')
        list_helpers_usernames = list(list_helper_group.user_set.values_list('username', flat=True))
        duplicated_usernames = [(username, username) for username in list_helpers_usernames]
        return (
            duplicated_usernames
        )

    def queryset(self, request, queryset):
        if (self.value()):
            return queryset.filter(mod__user__username=self.value())

@admin.register(Demon)
class DemonAdmin(admin.ModelAdmin):
    """Demon admin."""

    list_display = ('id', 'level', 'mode', 'category', 'level_id', 'demon_difficulty', 'length', 'type', 'all_position', 'rated_position', 'deathless_position', 'impossible_position', 'list_points', 'verification_video_embed', 'verification_video')
    search_fields = ('level', 'level_id')
    list_filter = ('demon_difficulty', 'mode', 'category', 'created', 'modified')

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    """Record admin."""

    list_display = ("id", "demon", "player", "deathless", "tentative_player", "accepted", "mod", "mods", "mod_notes", "datetime_checked")
    search_fields = ("player__user__username",)
    list_filter = ("accepted", "deathless", ProfileModFilter, "datetime_submit", "datetime_checked", "demon")

@admin.register(Changelog)
class ChangelogAdmin(admin.ModelAdmin):
    """Changelog admin."""

    list_display = ('id', 'demon', 'datetime', 'reason', 'rated_position', 'unrated_position', 'all_position', 'deathless_position', 'reason_option', 'reason_demon', 'datetime')
    search_fields = ('demon__level', 'reason')
    list_filter = ('reason_option', 'demon', 'datetime', )

@admin.register(Roulette)
class RouletteAdmin(admin.ModelAdmin):
    """Roulette admin."""

    list_display = ('id', 'name', 'player', 'mode', 'max_demons')
    search_fields = ('player__user__username', 'name')

@admin.register(RouletteDemon)
class RouletteDemonAdmin(admin.ModelAdmin):
    """RouletteDemon admin."""

    list_display = ('id', 'roulette', 'demon', 'num_level', 'percentage', 'demon_index')
    search_fields = ('demon__level', "roulette__name")

@admin.register(LevelPack)
class LevelPackAdmin(admin.ModelAdmin):
    """LevelPack admin."""

    list_display = ('id', 'name', 'color', 'mode', 'category')
    search_fields = ("name",)

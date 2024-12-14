# Django
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

# Models
from django.contrib.auth.models import User
from apps.users.models import Profile, Country, Notification, Team, TeamInvitation

# Views
from apps.users.views.views import LoginView

admin.site.login = LoginView.as_view()

class NullFilter(admin.SimpleListFilter):
    title = 'Id Discord'
    parameter_name = 'id_discord'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Sí'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.filter(id_discord__isnull=True)
        elif self.value() == 'no':
            return queryset.filter(id_discord__isnull=False)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Profile admin

    list_display = ("pk", "user", "verified", "id_discord", "discord", "platformer_list_points")
    list_display_links = ("pk", "user")
    list_editable = ("platformer_list_points",)
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone", "discord", "id_discord")
    list_filter = ("verified", NullFilter, "created", "modified")
    fieldsets = (
        ("Profile", {"fields": ("user", "picture", "banner")}),
        ("Extra info", {"fields": (("youtube_channel", "twitter", "twitch", "facebook", "id_discord", "discord", "phone"), "bio", "country", "classic_list_points", "classic_list_points_with_mods", "platformer_list_points", "platformer_challenge_list_points", "followers", "dark_mode", "verified", "language")}),
        ("Teams", {"fields": (("team", "claimable", "roulette_animation"))}),
        ("More info", {"fields": ("device", "preferences")}),
        ("Metadata", {"fields": ("created", "modified")}))
    readonly_fields = ("created", "modified")

class ProfileInline(admin.StackedInline):
    # Conexión con el Profile admin (para User admin)
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"

class UserAdmin(BaseUserAdmin):
    # Agrega el Profile admin al User admin
    inlines = (ProfileInline,)
    list_display = ("id", "username", "get_discord", "email", "get_verified", "display_groups")
    list_filter = ("groups", "profile__verified")
    ordering = ("-id",)

    def display_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    def get_discord(self, obj):
            return obj.profile.discord if hasattr(obj, 'profile') else None
    get_discord.short_description = 'Discord'
    def get_verified(self, obj):
            return obj.profile.verified if hasattr(obj, 'profile') else None
    get_verified.short_description = 'Verified'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Country admin."""

    list_display = ('id', 'country', 'platformer_list_points', 'picture', 'country_spanish', 'country_german', 'country_russian', 'country_czech', 'country_french')
    list_editable = ("picture",)
    search_fields = ('country',)
    list_filter = ('country',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""

    list_display = ('id', 'action', 'parameter', "demon_parameter", 'read', 'profile', 'profile_parameter')
    search_fields = ('profile__user__username',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Team admin."""

    list_display = ('id', 'name', 'owner', 'platformer_list_points')
    search_fields = ('name',)

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    """TeamInvitation admin."""

    list_display = ('id', 'team', 'player')
    search_fields = ('team',)
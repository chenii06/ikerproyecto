# Django
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, DurationField, Max, Exists

# Rest Framework
from rest_framework import status

# Functions
from apps.demonlist.functions import functions

# Mixins
from utils.mixins.translations import TranslationMixin

# Models
from apps.users.models import Profile, Team, Country

# Models (Proxy)
from apps.users.models.proxy import ExtendedProfile

# Utils
import datetime
import urllib


# Decorador que sirve para heredar métodos personalizados que pueden ayudar
class CustomMethodsMixin(TranslationMixin):
    # DATA (GET)
    def has_get_context_data(self):
        return hasattr(self, 'get_context_data') and callable(getattr(self, 'get_context_data'))



    def get_demon_filter_url(self, demon_filter):
        return urllib.parse.quote(demon_filter.encode()) if demon_filter else None

    def get_countries_without_korea(self):
        return Country.objects.exclude(country="North Korea").order_by(self.get_country_field(Country))


    # DATA (POST)
    def get_team_members(self, data):
        """Obtiene los miembros de un team específico."""
        team = Team.objects.get(id=data["id"])
        team_members = ExtendedProfile.objects.filter(team=team
                        ).annotate_if_owner(team).annotate_list_points(data).order_by(f"-list_points")
        if data["member"]:
            team_members = team_members.filter(user__username__icontains=data["member"])
        return team_members
    
    def get_time(self):
        """Obtiene los campos del tiempo y los convierte a datetime."""
        time_fields = ["hours", "minutes", "seconds", "milliseconds"]
        time_data = {field: self.request.POST.get(field, None) for field in time_fields}
        try:
            time = datetime.time(int(time_data["hours"]), int(time_data["minutes"]), int(time_data["seconds"]), int(time_data["milliseconds"][:3]) * 1000)
        except:
            time = datetime.time(0, 0, 0, 0)
        return time
    
    # DATA (BOTH)
    def get_position_field(self, category):
        """Obtiene el campo de posición basado en la categoría."""
        return f"{category}_position" if category != "all_demonlist" else "rated_position"

    def get_list_points(self, mode, category):
        if category and mode:
            return f"{mode}_{category}_list_points" if category != 'rated' else f"{mode}_list_points"
    
    def get_country_field(self, model):
        """Obtiene el campo de country_field dependiendo del idioma del usuario."""
        if model.__name__ == "Record":
            return (
                f"player__country__country_{self.request.global_context['language'].lower()}" 
                if self.request.global_context["language"] != "English" else "player__country__country"
            )
        if model.__name__ == "Country":
            return (
                f"country_{self.request.global_context['language'].lower()}" 
                if self.request.global_context["language"] != "English" else "country"
            )

    def get_country_object(self, country):
        """Obtiene la instancia de objeto 'Country' del country seleccionado."""
        if country:
            country = Country.objects.get(country=country)
        else:
            country = None
        return country

    # UTILS (POST)
    def assign_percentage_or_best_time(self, mode, record):
        """Asigna ya sea el porcentage o el best time al record creado dependiendo del modo del demon."""
        if mode == "classic":
            record.percentage = 100
        elif mode == "platformer":
            time = self.get_time()
            record.best_time = time
        return record

    def assign_image(self, data, profile, attr_name):
        """Asignación de imagen (foto de perfil o banner) al perfil."""
        if attr_name == "banner" and not(self.request.global_context["is_subscriber"]):
            return profile
        try:
            image = data[attr_name]
            if image is not None and functions.is_valid_image(image):
                old_image = getattr(profile, attr_name).path if getattr(profile, attr_name) else None
                if old_image and default_storage.exists(old_image):
                    default_storage.delete(old_image)
                file_path = default_storage.save(f"users/pictures/{profile.id}/{image.name}", ContentFile(image.read()))
                setattr(profile, attr_name, file_path)
        except:
            pass
        return profile

    def assign_profile_picture(self, data, profile):
        """Asignación de foto de perfil al perfil."""
        return self.assign_image(data, profile, "picture")

    def assign_profile_banner(self, data, profile):
        """Asignación de banner al perfil."""
        return self.assign_image(data, profile, "banner")

    def assign_social_media(self, data, profile):
        """Asignación de redes sociales al perfil."""
        social_media_links = {
            "youtube_channel": "https://www.youtube.com/@",
            "twitter": "https://twitter.com/",
            "twitch": "https://twitch.tv/",
            "facebook": "https://facebook.com/"
        }

        for platform, base_url in social_media_links.items():
            if data[platform].startswith(base_url) and data[platform] != base_url:
                setattr(profile, platform, data[platform])
            else:
                setattr(profile, platform, "")
        return profile

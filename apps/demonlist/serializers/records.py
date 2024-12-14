"""Record serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.demonlist.models import Record

# Utils
from functools import reduce
import operator


class RecordModelSerializer(serializers.ModelSerializer):
    """Record model serializer."""

    video_platform = serializers.CharField(source='_video_platform', read_only=True)
    player__user__id = serializers.CharField(source="player.user.id", read_only=True)
    player__user__username = serializers.CharField(source="player.user.username", read_only=True)
    player__team__id = serializers.CharField(source="player.team.id", read_only=True)
    player__team__name = serializers.CharField(source="player.team.name", read_only=True)
    player__country__picture = serializers.CharField(source="player.country.picture", read_only=True)

    best_time = serializers.SerializerMethodField()

    class Meta:
        """Meta class."""

        model = Record
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(RecordModelSerializer, self).__init__(*args, **kwargs)

        # Obtener el nombre del campo del contexto
        country_field = self.context.get('country_field', None)

        # Agregar el campo al serializer si se proporciona un nombre válido
        if country_field:
            country_field = ".".join(country_field.split("__"))
            self.fields['country_field'] = serializers.CharField(source=country_field, read_only=True)

    def get_best_time(self, obj):
        """Método para formatear el campo best_time."""
        if obj.best_time:
            # Formatear el tiempo para mostrar solo los primeros 3 dígitos de los milisegundos
            best_time_str = obj.best_time.strftime('%H:%M:%S.%f')[:-3]
            return best_time_str
        return None
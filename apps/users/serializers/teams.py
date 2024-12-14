"""Team serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.users.models import Team


class TeamModelSerializer(serializers.ModelSerializer):
    """Team model serializer."""

    class Meta:
        """Meta class."""

        model = Team
        fields = "__all__"

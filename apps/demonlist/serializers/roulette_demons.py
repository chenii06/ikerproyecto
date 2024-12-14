"""Roulette demon serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.demonlist.models import RouletteDemon


class RouletteDemonModelSerializer(serializers.ModelSerializer):
    """RouletteDemon model serializer."""

    class Meta:
        """Meta class."""

        model = RouletteDemon
        fields = ["stage", "num_level"]
"""Roulette serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.demonlist.models import Roulette

# Utils
from functools import reduce
import operator


class RouletteModelSerializer(serializers.ModelSerializer):
    """Roulette model serializer."""

    class Meta:
        """Meta class."""

        model = Roulette
        fields = "__all__"

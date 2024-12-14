"""Changelog serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.demonlist.models import Changelog


class ChangelogModelSerializer(serializers.ModelSerializer):
    """Changelog model serializer."""

    class Meta:
        """Meta class."""

        model = Changelog
        fields = "__all__"
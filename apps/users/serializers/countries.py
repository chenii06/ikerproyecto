"""Country serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.users.models import Country


class CountryModelSerializer(serializers.ModelSerializer):
    """Country model serializer."""

    class Meta:
        """Meta class."""

        model = Country
        fields = "__all__"

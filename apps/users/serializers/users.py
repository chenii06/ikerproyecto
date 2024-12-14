"""User serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from django.contrib.auth.models import User


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = User
        fields = "__all__"
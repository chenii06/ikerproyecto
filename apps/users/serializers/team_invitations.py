"""TeamInvitation serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.users.models import TeamInvitation


class TeamInvitationModelSerializer(serializers.ModelSerializer):
    """TeamInvitation model serializer."""

    class Meta:
        """Meta class."""

        model = TeamInvitation
        fields = "__all__"

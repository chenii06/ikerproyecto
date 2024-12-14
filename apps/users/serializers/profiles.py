"""Profile serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.users.models import Profile


class ProfileModelSerializer(serializers.ModelSerializer):
    """Profile model serializer."""
    user__id = serializers.CharField(source="user.id", read_only=True)
    user__username = serializers.CharField(source="user.username", read_only=True)
    list_points = serializers.FloatField(required=False)
    if_owner = serializers.BooleanField(required=False)
    country__country = serializers.CharField(source="country.country", read_only=True)

    class Meta:
        """Meta class."""

        model = Profile
        fields = [
            "id", "user__username", "user__id", "picture", "list_points", "if_owner",
            "picture", "country__country", "youtube_channel", "twitch", "twitter", "facebook"
        ]


class ProfileSelect2Serializer(serializers.ModelSerializer):
    """Profile select2 serializer."""
    text = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        """Meta class."""

        model = Profile
        fields = ["id", "text"]


class ProfileRouletteModelSerializer(serializers.ModelSerializer):
    """Profile Roulette model serializer."""
    user__id = serializers.CharField(source="user.id", read_only=True)
    user__username = serializers.CharField(source="user.username", read_only=True)
    in_roulette = serializers.BooleanField(required=False)

    class Meta:
        """Meta class."""

        model = Profile
        fields = [
            "id", "user__username", "user__id", "picture", "in_roulette",
        ]

class ProfileTeamModelSerializer(serializers.ModelSerializer):
    """Profile Team model serializer."""
    user__id = serializers.CharField(source="user.id", read_only=True)
    user__username = serializers.CharField(source="user.username", read_only=True)
    in_team = serializers.IntegerField(required=False)

    class Meta:
        """Meta class."""

        model = Profile
        fields = [
            "id", "user__username", "user__id", "picture", "in_team",
        ]

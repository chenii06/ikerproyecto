"""Demon serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from apps.demonlist.models import Demon


class DemonModelSerializer(serializers.ModelSerializer):
    """Demon model serializer."""

    new = serializers.BooleanField(required=False)
    changelog_position = serializers.IntegerField(required=False)
    order_position = serializers.IntegerField(required=False)
    real_verification_video_embed = serializers.CharField(required=False)
    uuid = serializers.IntegerField(required=False)

    class Meta:
        """Meta class."""

        model = Demon
        fields = "__all__"


class DemonSelect2Serializer(serializers.ModelSerializer):
    """Demon select2 serializer."""
    text = serializers.SerializerMethodField()

    class Meta:
        """Meta class."""

        model = Demon
        fields = ["id", "text"]

    def get_text(self, obj):
        return f"#{obj.order_position} - {obj.level}" if obj.order_position else obj.level


class DemonRouletteSerializer(serializers.ModelSerializer):
    """Demon roulette serializer."""
    photo__url = serializers.CharField(source='photo.url', read_only=True)

    class Meta:
        """Meta class."""

        model = Demon
        fields = [
            "level", "level_id", "verification_video", "photo__url", "category", "rated_position", 
            "unrated_position", "creator", "type", "demon_difficulty"
        ]

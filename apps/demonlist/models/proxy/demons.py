"""Demon proxy models."""

# Managers
from apps.demonlist.managers import ExtendedDemonManager

# Models
from apps.demonlist.models import Demon

class ExtendedDemon(Demon):
    """ListDemon proxy model."""

    objects = ExtendedDemonManager()

    class Meta:
        """Proxy model"""
        proxy = True
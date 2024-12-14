"""Profile proxy models."""

# Managers
from apps.users.managers import ProfileManager

# Models
from apps.users.models import Profile

class ExtendedProfile(Profile):
    """ListProfile proxy model."""

    objects = ProfileManager()

    class Meta:
        """Proxy model"""
        proxy = True

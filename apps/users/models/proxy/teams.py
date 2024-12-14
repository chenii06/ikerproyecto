"""Team proxy models."""

# Managers
from apps.users.managers import TeamManager

# Models
from apps.users.models import Team

class ExtendedTeam(Team):
    """ListTeam proxy model."""

    objects = TeamManager()

    class Meta:
        """Proxy model"""
        proxy = True

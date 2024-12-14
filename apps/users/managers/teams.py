"""Team managers."""

# Managers
from utils.managers import StatsManager

# Querysets
from apps.users.querysets import TeamQuerySet

class TeamManager(StatsManager):
    """DJANGO METHODS"""
    def get_queryset(self):
        return TeamQuerySet(self.model, using=self._db)

    """EXTENDED METHODS"""

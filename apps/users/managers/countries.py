"""Country managers."""

# Managers
from utils.managers import StatsManager

# Querysets
from apps.users.querysets import CountryQuerySet

class CountryManager(StatsManager):
    """DJANGO METHODS"""
    def get_queryset(self):
        return CountryQuerySet(self.model, using=self._db)

    """EXTENDED METHODS"""

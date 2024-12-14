"""Profile managers."""

# Managers
from utils.managers import StatsManager

# Querysets
from apps.users.querysets import ProfileQuerySet

class ProfileManager(StatsManager):
    """DJANGO METHODS"""
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db)

    """EXTENDED METHODS"""
    # FILTERS
    def filter_by_country(self, data):
        return self.get_queryset().filter_by_country(data)
    
    # ANNOTATES
    def annotate_if_owner(self, team):
        return self.get_queryset().annotate_if_owner(team)

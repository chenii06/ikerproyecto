"""Stats managers."""

# Managers
from django_cte import CTEManager

# Querysets
from utils.querysets import StatsQuerySet

class StatsManager(CTEManager):
    """DJANGO METHODS"""
    def get_queryset(self):
        return StatsQuerySet(self.model, using=self._db)

    """EXTENDED METHODS"""
    # FILTERS
    def filter_with_list_points(self, list_points):
        return self.get_queryset().filter_with_list_points(list_points)

    def filter_by_search(self, data):
        return self.get_queryset().filter_by_search(data)

    def filter_by_list(self, data):
        return self.get_queryset().filter_by_list(data)

    # ANNOTATES
    def annotate_position(self, data):
        return self.get_queryset().annotate_position(data)

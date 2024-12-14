"""Record managers."""

# Django
from django.db import models
from django.db.models import Case, When, CharField, Value

# Querysets
from apps.demonlist.querysets import RecordQuerySet

class RecordManager(models.Manager):
    """DJANGO METHODS"""
    def get_queryset(self):
        return RecordQuerySet(self.model, using=self._db)

    """EXTENDED METHODS"""
    # FILTERS
    def filter_by_category_list(self, data):
        return self.get_queryset().filter_by_category_list(data)

    def exclude_tentative_player(self):
        return self.get_queryset().exclude_tentative_player()

    # ANNOTATES
    def annotate_video_platform(self):
        return self.get_queryset().annotate_video_platform()

    def annotate_order_position(self, category):
        return self.get_queryset().annotate_order_position(category)

    def annotate_category_position(self, category):
        return self.get_queryset().annotate_category_position(category)

    def annotate_category_list_points(self, category):
        return self.get_queryset().annotate_category_list_points(category)

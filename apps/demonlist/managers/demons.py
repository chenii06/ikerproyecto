"""Demon managers."""

# Django
from django.db import models

# Querysets
from apps.demonlist.querysets import DemonQuerySet

class DemonManager(models.Manager):
    """Demon manager.
    
    Usado para no filtrar los demons que estén inactivos
    """

    def get_queryset(self):
        return super().get_queryset()

    def filter(self, *args, **kwargs):
        if 'removed' not in kwargs:
            kwargs['removed'] = False
        return super().filter(*args, **kwargs)

    def filter_with_removed(self, *args, **kwargs):
        return super().filter(*args, **kwargs)

    def all(self):
        return self.get_queryset().filter(removed=False)

    def exclude(self, *args, **kwargs):
        if 'removed' not in kwargs:
            kwargs['removed'] = False
        return super().exclude(*args, **kwargs)

    def exclude_with_removed(self, *args, **kwargs):
        return super().exclude(*args, **kwargs)

    def order_by(self, *field_names):
        return super().order_by(*field_names)

    def order_by_with_removed(self, *field_names):
        return self.get_queryset().order_by(*field_names)


class ForeignKeyDemonManager(models.Manager):
    """Demon manager.
    
    Usado para no filtrar los demons que estén inactivos siendo el demon una llave foránea
    """
    
    def get_queryset(self):
        return super().get_queryset()

    def filter(self, *args, **kwargs):
        if 'demon__removed' not in kwargs:
            kwargs['demon__removed'] = False
        return super().filter(*args, **kwargs)

    def all(self):
        return self.get_queryset().filter(demon__removed=False)

    def exclude(self, *args, **kwargs):
        if 'demon__removed' not in kwargs:
            kwargs['demon__removed'] = False
        return super().exclude(*args, **kwargs)

    def order_by(self, *field_names):
        return self.get_queryset().filter(demon__removed=False).order_by(*field_names)


class ExtendedDemonManager(DemonManager):
    """DJANGO METHODS"""
    def get_queryset(self):
        return DemonQuerySet(self.model, using=self._db)

    """EXTENDED METHODS"""
    # FILTERS
    def filter_with_removed(self, *args, **kwargs):
        return self.get_queryset().filter_with_removed(*args, **kwargs)

    def filter_by_time_machine_date(self, mode, position_field, time_machine_date):
        return self.get_queryset().filter_by_time_machine_date(mode, position_field, time_machine_date)

    def filter_by_category_list(self, mode, category):
        return self.get_queryset().filter_by_category_list(mode, category)

    def filter_by_categories(self, AVAILABLE_CATEGORIES):
        return self.get_queryset().filter_by_categories(AVAILABLE_CATEGORIES)

    def filter_demons_allowed_to_submit(self, mode, category, LIMITS):
        return self.get_queryset().filter_demons_allowed_to_submit(mode, category, LIMITS)

    def filter_by_search(self, search):
        return self.get_queryset().filter_by_search(search)

    def filter_by_status(self, data):
        return self.get_queryset().filter_by_status(data)

    def filter_generics(self, **kwargs):
        return self.get_queryset().filter_generics(**kwargs)


    # ANNOTATES
    def annotate_changelog_position(self, time_machine_date):
        return self.get_queryset().annotate_changelog_position(time_machine_date)

    def annotate_new(self):
        return self.get_queryset().annotate_new()
    
    def annotate_order_position(self, category):
        return self.get_queryset().annotate_order_position(category)

    def annotate_alternative_order_position(self, category):
        return self.get_queryset().annotate_alternative_order_position(category)

    def annotate_category_position(self, category):
        return self.get_queryset().annotate_category_position(category)

    def annotate_category_list_points(self, category):
        return self.get_queryset().annotate_category_list_points(category)

    def annotate_uuid(self):
        return self.get_queryset().annotate_uuid()

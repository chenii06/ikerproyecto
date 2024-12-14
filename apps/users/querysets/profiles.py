# Django
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, DurationField, Max, Exists

# Querysets
from utils.querysets import StatsQuerySet


class ProfileQuerySet(StatsQuerySet):

    # FILTERS
    def filter_by_country(self, data):
        return self.filter(country__country=data["country_filter"])

    # ANNOTATES
    def annotate_if_owner(self, team):
        return self.annotate(if_owner=Case(
                When(id=team.owner.id, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ))

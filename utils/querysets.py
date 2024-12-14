# Django
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, DurationField, Max, Exists, QuerySet
from django.db.models.functions import Rank, Cast
from django_cte import CTEQuerySet


class StatsQuerySet(CTEQuerySet, QuerySet):

    # FILTERS
    def filter_with_list_points(self, list_points):
        return self.filter(**{f"{list_points}__gte": 1})
    
    def filter_with_list_points_with_mods(self, list_points):
        return self.filter(**{f"{list_points}_with_mods__gte": 1})

    def filter_by_search(self, data):
        if data["status_filter"] == "Nations":
            search_field = data['country_field']
        elif data["status_filter"] == "Teams":
            search_field = "name"
        elif data["status_filter"] == "Individual":
            search_field = "user__username"
        return self.filter(**{f"{search_field}__icontains": data["search_filter"]})

    def filter_by_list(self, data):
        if data["list_filter"] and data.get("with_mods"):
            queryset = self.filter_with_list_points_with_mods(
                data["list_points"]
            ).annotate_position(data).annotate_list_points(data)       
        elif data["list_filter"]:
            queryset = self.filter_with_list_points(
                data["list_points"]
            ).annotate_position(data).annotate_list_points(data)
        else:
            queryset = self.none()
        return queryset

    # ANNOTATES
    def annotate_position(self, data):
        if data.get("with_mods"):
            queryset = self.annotate(
                position=Window(expression=Rank(), order_by=F(f"{data['list_points']}_with_mods").desc())
            ).order_by(f"-{data['list_points']}_with_mods")
        else:
            queryset = self.annotate(
                position=Window(expression=Rank(), order_by=F(data["list_points"]).desc())
            ).order_by(f"-{data['list_points']}")
        return queryset

    def annotate_list_points(self, data):
        if data.get("with_mods"):
            return self.annotate(list_points=F(f"{data['list_points']}_with_mods"))
        else:
            return self.annotate(list_points=F(data["list_points"]))

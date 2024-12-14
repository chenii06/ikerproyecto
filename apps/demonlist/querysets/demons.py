# Django
from django.conf import settings
from django.db.models import QuerySet, OuterRef, Subquery, Case, When, Value, BooleanField, Q, F, IntegerField
from django.db.models.functions import Concat
from django.utils import timezone
import datetime

# Functions
from apps.demonlist.functions.demons import ExtractUUID


class CustomQueryset(QuerySet):
    FILTERING_FIELDS = {
        "demon_difficulty": "in",
        "verification_status": "in",
    }

    def filter_generics(self, field, value, filter_action):
        queryset = self
        if value:
            queryset = queryset.filter(**{f"{field}__{filter_action}": value})
        return queryset


class DemonQuerySet(CustomQueryset):
    """DJANGO METHODS"""
    def filter(self, *args, **kwargs):
        if 'removed' not in kwargs:
            kwargs['removed'] = False
        return super().filter(*args, **kwargs)

    def filter_with_removed(self, *args, **kwargs):
        return super().filter(*args, **kwargs)

    def all(self):
        return self.filter(removed=False)

    def exclude(self, *args, **kwargs):
        if 'removed' not in kwargs:
            kwargs['removed'] = False
        return super().exclude(*args, **kwargs)

    def exclude_with_removed(self, *args, **kwargs):
        return super().exclude(*args, **kwargs)

    def order_by(self, *field_names):
        return super().order_by(*field_names)

    def order_by_with_removed(self, *field_names):
        return self.order_by(*field_names)

    """FILTERS"""
    def filter_by_time_machine_date(self, mode, position_field, time_machine_date):
        queryset = self.filter(mode=mode, created__lte=time_machine_date)
        queryset = queryset.annotate_changelog_position(mode, position_field, time_machine_date)
        return queryset.filter(changelog_position__isnull=False).order_by('changelog_position')

    def filter_by_category_list(self, mode, category):
        queryset = self
        if category == "all":
            queryset = queryset.filter(mode=mode).exclude(all_position__isnull=True).order_by("all_position")
        elif category == "challenge":
            queryset = queryset.filter(mode=mode, category=category).order_by("challenge_position")
        elif category == "all_demonlist":
            if mode:
                queryset = queryset.filter(mode=mode)
            queryset = queryset.filter(category="rated").order_by("-downloads")
        elif category == "easiest":
            queryset = queryset.filter(mode=mode, category="rated", easiest_position__isnull=False).order_by("easiest_position")
        elif category == "shitty":
            queryset = queryset.filter(mode=mode, category=category).order_by("shitty_position")
        elif category == "future":
            queryset = queryset.filter(category=category).order_by("future_position")
        elif category == "tiny":
            queryset = queryset.filter(mode=mode, category=category).order_by("tiny_position")
        elif category == "deathless":
            queryset = queryset.filter(mode=mode, deathless=True).order_by("deathless_position")
        elif category == "impossible":
            queryset = queryset.filter(mode=mode, impossible_position__isnull=False).order_by("impossible_position")
        elif category == "spam":
            queryset = queryset.filter(mode=mode, category=category).order_by("spam_position")
        elif category == "impossible_tiny":
            queryset = queryset.filter(mode=mode, category=category).order_by("impossible_tiny_position")
        elif category == "rated":
            queryset = queryset.filter(mode=mode, category=category).exclude(rated_position__isnull=True).order_by("rated_position")
        elif category == "unrated":
            queryset = queryset.filter(mode=mode, category=category).exclude(unrated_position__isnull=True).order_by("unrated_position")
        return queryset

    def filter_by_categories(self, AVAILABLE_CATEGORIES):
        query = Q()

        for CATEGORY in AVAILABLE_CATEGORIES:
            query |= Q(**{f"{CATEGORY}_position__isnull": False })
        return self.filter(query)
    
    def filter_demons_allowed_to_submit(self, mode, category, LIMITS):
        self = self.filter_by_category_list(mode, category)
        query = Q(**{f"{category}_position__lte": LIMITS[mode][category], "mode": mode})
        return self.filter(query)
    
    def filter_by_search(self, search):
        queryset = self
        if search:
            queryset = queryset.filter(level__icontains=search)
        return queryset

    def filter_by_status(self, data):
        queryset = self
        if data["status"] == ["Completed"]:
            queryset = queryset.filter(id__in=data["record_demons"])
        elif data["status"] == ["Not completed"]:
            queryset = queryset.exclude(id__in=data["record_demons"])
        return queryset
    
    def handler_filter_generics(self, **kwargs):
        queryset = self
        for field, filter_action in self.FILTERING_FIELDS.items():
            if kwargs.get(field):
                queryset = queryset.filter_generics(field, kwargs.get(field), filter_action)
        return queryset


    """ANNOTATES"""
    def annotate_changelog_position(self, mode, position_field, time_machine_date):
        from apps.demonlist.models import Changelog
        latest_changelogs = Changelog.objects.filter(
            demon=OuterRef('pk'),
            demon__mode=mode,
            **{f'{position_field}__isnull': False},
            datetime__lte=time_machine_date
        ).order_by('-id')[:1]
        return self.annotate(
            changelog_position=Subquery(latest_changelogs.values(position_field)[:1])
        )

    def annotate_new(self, category):
        from apps.demonlist.models import Changelog
        week_duration = timezone.now() - timezone.timedelta(weeks=1)
        return self.annotate(
            last_changelog_datetime=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('datetime')[:1]
            ),
            last_changelog_reason_option=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('reason_option')[:1]
            ),
            last_changelog_reason_demon=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values('reason_demon')[:1]
            ),
            last_changelog_order_position=Subquery(
                Changelog.objects.filter(demon=OuterRef("id")).order_by('-datetime').values(f'{category}_position')[:1]
            ),
            new=Case(
                When(
                    Q(all_position__isnull=False) | Q(challenge_position__isnull=False) | Q(shitty_position__isnull=False) | Q(tiny_position__isnull=False) | Q(deathless_position__isnull=False) | Q(impossible_position__isnull=False) | Q(spam_position__isnull=False) | Q(impossible_tiny_position__isnull=False),
                    created__gt=week_duration,
                    then=Value(True)
                ),
                When(
                    last_changelog_datetime__gt=week_duration,
                    last_changelog_reason_option__in=["added_to_list", "rated", "unrated", "challenge", "shitty", "tiny", "deathless", "impossible", "spam", "impossible_tiny", "all"],
                    last_changelog_reason_demon=F("id"),
                    last_changelog_order_position__isnull=False,
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        )
    
    def annotate_order_position(self, category):
        if category == "deathless":
            cases = [
                When(Q(deathless=True), then=F('deathless_position'))
            ]
        elif category == "impossible":
            cases = [
                When(Q(impossible_position__isnull=False), then=F('impossible_position'))
            ]
        elif category == "all":
            cases = [
                When(Q(all_position__isnull=False), then=F('all_position'))
            ]
        else:
            cases = [
                When(Q(category=cat), then=F(f'{cat}_position'))
                for cat in settings.CATEGORIES if not(cat in ["deathless", "impossible", "all"])
            ]
        return self.annotate(
            order_position=Case(*cases, output_field=IntegerField())
        )

    def annotate_alternative_order_position(self, category):
        if category == "deathless":
            cases = [When(Q(deathless=True), then=F('deathless_position'))]
        elif category == "impossible":
            cases = [When(Q(impossible_position__isnull=False), then=F('impossible_position'))]
        else:
            cases = [
                When(Q(category=cat), then=F(f'{cat}_position'))
                for cat in settings.ALTERNATIVE_CATEGORIES if not(cat in ["rated", "unrated", "deathless", "impossible"])
            ]
        return self.annotate(
            order_position=Case(
                *cases,
                When(Q(category="rated") | Q(category="unrated"), then=F(f"all_position")),
                output_field=IntegerField()
            )
        )

    def annotate_category_position(self, category):
        if category == "deathless":
            cases = [When(Q(deathless=True), then=F('deathless_position'))]
        elif category == "impossible":
            cases = [When(Q(impossible_position__isnull=False), then=F('impossible_position'))]
        else:
            cases = [When(Q(category=category), then=F(f'{category}_position'))]
        return self.annotate(
            category_position=Case(*cases, output_field=IntegerField())
        )

    def annotate_category_list_points(self, category):
        if category == "deathless":
            category_list_points = "deathless_list_points"
        elif category == "impossible":
            category_list_points = "impossible_list_points"
        elif category == "all":
            category_list_points = "all_list_points"
        else:
            category_list_points = "list_points"
        return self.annotate(category_list_points=F(category_list_points))

    def annotate_uuid(self):
        return self.annotate(
            uuid=ExtractUUID(F('verification_video_embed'))
        )

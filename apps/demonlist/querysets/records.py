# Django
from django.conf import settings
from django.db.models import Q, QuerySet, Case, When, Value, CharField, IntegerField, F


class RecordQuerySet(QuerySet):

    # FILTERS
    def filter_by_category_list(self, data):
        if data["category"] == "deathless":
            return self.filter(
                player=data["user"].profile,
                accepted=True,
                demon__mode=data["mode"],
                demon__deathless=True,
                demon__deathless_position__isnull=False,
                demon__removed=False
            )
        elif data["category"] == "all":
            return self.filter(
                player=data["user"].profile,
                accepted=True,
                demon__mode=data["mode"],
                demon__all_position__isnull=False,
                demon__removed=False
            )
        else:
            return self.filter(
                player=data["user"].profile,
                accepted=True,
                demon__mode=data["mode"],
                demon__category=data["category"],
                demon__removed=False
            )

    def exclude_tentative_player(self):
        return self.filter(tentative_player__isnull=True)

    # ANNOTATES
    def annotate_video_platform(self):
        return self.annotate(_video_platform=Case(
            When(video__regex=r'(https?://)?(www\.)?(m\.)?(youtube\.com|youtu\.be)/(watch\?v=)?([^&\n]+)', then=Value('YouTube')),
            When(video__regex=r'(https?://)?(www\.)?twitch\.(tv|com)/.+', then=Value('Twitch')),
            When(video__regex=r'(https?://)?clips\.twitch\.tv/.+', then=Value('Twitch')),
            When(video__regex=r'(https?://)?(www\.)?facebook\.(com)/.+', then=Value('Facebook')),
            When(video__regex=r'(https?://)?drive\.google\.com/.+', then=Value('Drive')),
            default=Value(''),
            output_field=CharField()
        ))
    
    def annotate_order_position(self, category):
        if category == "deathless":
            query = self.annotate(
                order_position=Case(
                    When(Q(demon__deathless=True), then="demon__deathless_position"),
                )
            )
        elif category == "impossible":
            query = self.annotate(
                order_position=Case(
                    When(Q(demon__impossible_position__isnull=False), then="demon__impossible_position"),
                )
            )
        else:
            query = self.annotate(
                order_position=Case(
                    When(Q(demon__category="rated"), then="demon__rated_position"),
                    When(Q(demon__category="unrated"), then="demon__unrated_position"),
                    When(Q(demon__category="challenge"), then="demon__challenge_position"),
                    When(Q(demon__category="shitty"), then="demon__shitty_position"),
                    When(Q(demon__category="tiny"), then="demon__tiny_position"),
                    When(Q(demon__category="spam"), then="demon__spam_position"),
                    When(Q(demon__category="impossible_tiny"), then="demon__impossible_tiny_position"),
                    When(Q(demon__category="all"), then="demon__all_position"),
                    output_field=IntegerField(),
                )
            )
        return query

    def annotate_order_position(self, category):
        if category == "deathless":
            cases = [When(Q(demon__deathless=True), then=F('demon__deathless_position'))]
        elif category == "impossible":
            cases = [When(Q(demon__impossible_position__isnull=False), then=F('demon__impossible_position'))]
        else:
            cases = [
                When(Q(demon__category=cat), then=F(f'demon__{cat}_position'))
                for cat in settings.CATEGORIES if not(cat in ["deathless", "impossible"])
            ]
        return self.annotate(
            order_position=Case(*cases, output_field=IntegerField())
        )

    def annotate_category_position(self, category):
        if category == "deathless":
            cases = [When(Q(demon__deathless=True), then=F('demon__deathless_position'))]
        elif category == "impossible":
            cases = [When(Q(demon__impossible_position__isnull=True), then=F('demon__impossible_position'))]
        else:
            cases = [When(Q(demon__category=category), then=F(f'demon__{category}_position'))]
        return self.annotate(
            category_position=Case(*cases, output_field=IntegerField())
        )

    def annotate_category_list_points(self, category):
        if category == "deathless":
            category_list_points = "demon__deathless_list_points"
        elif category == "impossible":
            category_list_points = "demon__impossible_list_points"
        elif category == "all":
            category_list_points = "demon__all_list_points"
        else:
            category_list_points = "demon__list_points"
        return self.annotate(category_list_points=F(category_list_points))

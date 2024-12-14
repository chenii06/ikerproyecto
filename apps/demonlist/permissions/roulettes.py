"""Records permissions."""

# Django
from django.db.models import Q

# Django REST Framework
from rest_framework.permissions import BasePermission

# Models
from django.contrib.auth.models import Group
from apps.demonlist.models import Roulette


class IsOwnerRoulette(BasePermission):
    """Verificar que sea dueño de la ruleta o, que por lo menos, haya sido invitado."""

    def has_object_permission(self, request, view, obj):
        return (request.user.profile == obj.player) or (request.user.profile in obj.players_to_share.all())


class IsLimitedRoulette(BasePermission):
    """Verificar si ya llegó al límite de ruletas disponibles."""

    def has_permission(self, request, view):
        roulettes = Roulette.objects.filter(
            Q(player=request.user.profile) | Q(players_to_share__in=[request.user.profile])
        ).distinct().count()
        
        subscriber_group = Group.objects.filter(name__in=[
            'Subscriber'
        ])
        if request.user.groups.filter(pk__in=subscriber_group.values_list('pk', flat=True)).exists():
            return (roulettes < 20)
        else:
            return (roulettes < 2)

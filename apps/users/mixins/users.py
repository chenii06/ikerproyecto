# Django
from django.contrib.auth.mixins import UserPassesTestMixin

# Models
from django.contrib.auth.models import User, Group


# Decorador que sirve para darle acceso a ciertas vistas solo a los Admins
class ListAdminMixin(UserPassesTestMixin):
    def test_func(self):
        is_admin = False
        grupos = Group.objects.filter(name__in=[
                'List Admin',
            ])
        if self.request.user.groups.filter(pk__in=grupos.values_list('pk', flat=True)).exists():
            is_admin = True
        return self.request.user.is_authenticated and is_admin


# Decorador que sirve para darle acceso a ciertas vistas solo a los Mods o Admins
class ListModMixin(UserPassesTestMixin):
    def test_func(self):
        is_mod = False
        grupos = Group.objects.filter(name__in=[
                'List Admin',
                'Classic Rated List Leader',
                'Classic Unrated List Leader',
                'Classic Tiny List Leader',
                'Classic Shitty List Leader',
                'Classic Spam List Leader',
                'Classic Impossible Tiny List Leader',
                'Platformer Rated List Leader',
                'Platformer Unrated List Leader',
                'Platformer Challenge List Leader',
                'Platformer Deathless List Leader',
                'Platformer Impossible List Leader',
                'Platformer Tiny List Leader',
                'TPL List Leader',
                'All DemonList Editor'
            ])
        if self.request.user.groups.filter(pk__in=grupos.values_list('pk', flat=True)).exists():
            is_mod = True
        return self.request.user.is_authenticated and is_mod


# Decorador que sirve para darle acceso a ciertas vistas solo a los List Helpers, Mods o Admins
class ListHelperMixin(UserPassesTestMixin):
    def test_func(self):
        is_helper = False
        grupos = Group.objects.filter(name__in=[
                'List Admin',
                'Classic Rated List Leader',
                'Classic Unrated List Leader',
                'Classic Tiny List Leader',
                'Classic Shitty List Leader',
                'Classic Spam List Leader',
                'Classic Impossible Tiny List Leader',
                'Platformer Rated List Leader',
                'Platformer Unrated List Leader',
                'Platformer Challenge List Leader',
                'Platformer Deathless List Leader',
                'Platformer Impossible List Leader',
                'Platformer Tiny List Leader',
                'TPL List Leader',
                'Classic Rated List Helper',
                'Classic Unrated List Helper',
                'Classic Tiny List Helper',
                'Classic Spam List Helper',
                'Classic Impossible Tiny List Helper',
                'Platformer Rated List Helper',
                'Platformer Unrated List Helper',
                'Platformer Challenge List Helper',
                'Platformer Deathless List Helper',
                'Platformer Impossible List Helper',
                'Platformer Tiny List Helper',
                'TPL List Helper',
                'All DemonList Editor'
            ])
        if self.request.user.groups.filter(pk__in=grupos.values_list('pk', flat=True)).exists():
            is_helper = True
        return self.request.user.is_authenticated and is_helper
    
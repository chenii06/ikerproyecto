"""Records permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission


class IsListHelper(BasePermission):
    """Verificar que sea List Helper."""

    def has_object_permission(self, request, view, obj):
        return self.request.global_context['is_list_helper']

class IsListMod(BasePermission):
    """Verificar que sea List Mod."""

    def has_object_permission(self, request, view, obj):
        return self.request.global_context['is_list_leader'] or self.request.global_context['is_list_editor']

"""Records permissions."""

# Django REST Framework
from rest_framework.permissions import BasePermission


class IsRecordOwnerAndAccepted(BasePermission):
    """Verificar que sea dueño del record y, además, que sea un record aceptado."""

    def has_object_permission(self, request, view, obj):
        return obj.accepted and obj.player == request.user.profile

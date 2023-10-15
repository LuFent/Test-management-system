from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import RegistrationToken
import datetime


class RegistrationTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.query_params.get("token")

        if not token:
            raise PermissionDenied("No Token")

        try:
            token = RegistrationToken.objects.get(token=token)
            now = datetime.datetime.now().timestamp()
            if now > token.expired_at.timestamp():
                raise PermissionDenied("Token has expired")

        except RegistrationToken.DoesNotExist:
            raise PermissionDenied("No such Token")

        return True

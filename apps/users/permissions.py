from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import User


class IsAdmin(BasePermission):
    """BR-4: Faqat role='admin' bo'lgan foydalanuvchilarga ruxsat beradi."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN
        )


class IsAdminOrReadOnly(BasePermission):
    """BR-4: GET, HEAD, OPTIONS — hammaga; o'zgartirish metodlari — faqat adminga."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN
        )

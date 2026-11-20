from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Faqat role='admin' yoki is_superuser/is_staff bo'lgan foydalanuvchilarga ruxsat beradi.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (getattr(request.user, 'role', None) == 'admin' or request.user.is_staff or request.user.is_superuser)
        )


class IsAdminOrReadOnly(BasePermission):
    """
    GET, HEAD, OPTIONS so'rovlar hammaga ochiq;
    Qolgan yozish amallari faqat admin uchun.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (getattr(request.user, 'role', None) == 'admin' or request.user.is_staff or request.user.is_superuser)
        )

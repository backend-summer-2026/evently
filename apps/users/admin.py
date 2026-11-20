from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-date_joined"]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "role",
        "telegram_chat_id",
        "is_staff",
        "is_active",
    ]
    list_filter = ["role", "is_staff", "is_superuser", "is_active"]
    search_fields = ["email", "first_name", "last_name", "phone_number"]

    # Standart UserAdmin'dagi username maydoni o'rniga email va loyiha maydonlari
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "phone_number")},
        ),
        (
            _("Role & Telegram"),
            {"fields": ("role", "telegram_chat_id", "telegram_link_token")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

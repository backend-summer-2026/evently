from django.contrib import admin

from apps.events.models import Event, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ("created_at", "cancelled_at")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "event_type",
        "status",
        "start_at",
        "end_at",
        "capacity",
        "created_by",
    )
    list_filter = ("event_type", "status")
    search_fields = ("title",)
    inlines = (RegistrationInline,)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event",
        "status",
        "reminder_sent",
        "created_at",
        "cancelled_at",
    )
    list_filter = ("status", "reminder_sent")
    search_fields = ("user__email", "event__title")

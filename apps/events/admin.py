from django.contrib import admin
from apps.events.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'event_type',
        'start_at',
        'end_at',
        'capacity',
        'status',
        'created_by',
        'created_at',
    )
    list_filter = ('event_type', 'status', 'start_at')
    search_fields = ('title', 'description', 'location')
    ordering = ('-start_at',)
    readonly_fields = ('created_at', 'updated_at')

import django_filters
from django.utils import timezone
from apps.events.models import Event


class EventFilter(django_filters.FilterSet):
    event_type = django_filters.CharFilter(field_name='event_type', lookup_expr='exact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    upcoming = django_filters.BooleanFilter(method='filter_upcoming')

    class Meta:
        model = Event
        fields = ['event_type', 'status', 'upcoming']

    def filter_upcoming(self, queryset, name, value):
        if value:
            return queryset.filter(start_at__gt=timezone.now())
        return queryset

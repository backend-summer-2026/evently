import django_filters
from django.db.models import QuerySet
from django.utils import timezone

from apps.events.models import Event


class EventFilter(django_filters.FilterSet):
    upcoming = django_filters.BooleanFilter(method="filter_upcoming")

    class Meta:
        model = Event
        fields = ("event_type", "status")

    def filter_upcoming(
        self,
        queryset: QuerySet[Event],
        name: str,
        value: bool,
    ) -> QuerySet[Event]:
        if value:
            return queryset.filter(start_at__gt=timezone.now())
        return queryset

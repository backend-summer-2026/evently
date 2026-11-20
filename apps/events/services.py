from django.db import transaction
from config.exceptions import BusinessLogicError
from apps.events.models import Event, EventStatus


@transaction.atomic
def create_event(*, title, description, event_type, location, start_at, end_at, capacity=None, created_by=None) -> Event:
    return Event.objects.create(
        title=title,
        description=description,
        event_type=event_type,
        location=location,
        start_at=start_at,
        end_at=end_at,
        capacity=capacity,
        created_by=created_by,
        status=EventStatus.OPEN
    )


@transaction.atomic
def update_event(*, event_id: int, **fields) -> Event:
    event = Event.objects.select_for_update().get(id=event_id)

    if 'capacity' in fields:
        new_capacity = fields['capacity']
        if new_capacity is not None and new_capacity < event.registered_count:
            raise BusinessLogicError(
                detail="Joylar soni hozirgi qatnashuvchilar sonidan kam bo‘lishi mumkin emas.",
                code="capacity_too_low"
            )

    for field, value in fields.items():
        setattr(event, field, value)

    event.save()
    return event


@transaction.atomic
def close_event(*, event_id: int) -> Event:
    event = Event.objects.select_for_update().get(id=event_id)
    event.status = EventStatus.CLOSED
    event.save(update_fields=['status', 'updated_at'])
    return event

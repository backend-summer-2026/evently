from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from apps.events.models import Event, Registration

EVENTS_URL = "/api/v1/events/"


def _valid_event_payload() -> dict:
    now = timezone.now()
    return {
        "title": "Django REST Framework asoslari",
        "description": "API yaratish bo'yicha amaliy master-klass.",
        "event_type": Event.EventType.MASTERCLASS,
        "location": "IT Park, 3-qavat, 301-xona",
        "start_at": (now + timedelta(days=2)).isoformat(),
        "end_at": (now + timedelta(days=2, hours=3)).isoformat(),
        "capacity": 30,
    }


def _create_event(admin_user) -> Event:
    now = timezone.now()
    return Event.objects.create(
        title="Boshlang'ich tadbir",
        description="Tavsif",
        event_type=Event.EventType.SEMINAR,
        location="Toshkent",
        start_at=now + timedelta(days=3),
        end_at=now + timedelta(days=3, hours=2),
        capacity=25,
        created_by=admin_user,
    )


@pytest.mark.django_db
def test_admin_can_create_event(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(EVENTS_URL, _valid_event_payload(), format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Django REST Framework asoslari"
    assert response.data["status"] == Event.Status.OPEN
    assert response.data["created_by"] == admin_user.id


@pytest.mark.django_db
def test_regular_user_cannot_create_event(api_client, user):
    api_client.force_authenticate(user=user)
    response = api_client.post(EVENTS_URL, _valid_event_payload(), format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Event.objects.count() == 0


@pytest.mark.django_db
def test_anonymous_user_cannot_create_event(api_client):
    response = api_client.post(EVENTS_URL, _valid_event_payload(), format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Event.objects.count() == 0


@pytest.mark.django_db
def test_admin_can_update_and_delete_event(api_client, admin_user):
    event = _create_event(admin_user)
    detail_url = f"{EVENTS_URL}{event.id}/"

    api_client.force_authenticate(user=admin_user)
    patch_response = api_client.patch(
        detail_url,
        {"title": "Yangilangan sarlavha"},
        format="json",
    )
    assert patch_response.status_code == status.HTTP_200_OK
    event.refresh_from_db()
    assert event.title == "Yangilangan sarlavha"

    delete_response = api_client.delete(detail_url)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Event.objects.filter(id=event.id).exists()


@pytest.mark.django_db
def test_regular_user_cannot_update_or_delete_event(api_client, user, admin_user):
    event = _create_event(admin_user)
    detail_url = f"{EVENTS_URL}{event.id}/"

    api_client.force_authenticate(user=user)
    patch_response = api_client.patch(
        detail_url,
        {"title": "Buzilgan sarlavha"},
        format="json",
    )
    assert patch_response.status_code == status.HTTP_403_FORBIDDEN

    delete_response = api_client.delete(detail_url)
    assert delete_response.status_code == status.HTTP_403_FORBIDDEN

    event.refresh_from_db()
    assert event.title == "Boshlang'ich tadbir"


@pytest.mark.django_db
def test_cannot_create_event_with_end_before_start(api_client, admin_user):
    now = timezone.now()
    payload = _valid_event_payload()
    payload["start_at"] = (now + timedelta(days=2, hours=3)).isoformat()
    payload["end_at"] = (now + timedelta(days=2)).isoformat()

    api_client.force_authenticate(user=admin_user)
    response = api_client.post(EVENTS_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "end_at" in response.data


@pytest.mark.django_db
def test_cannot_create_event_in_the_past(api_client, admin_user):
    now = timezone.now()
    payload = _valid_event_payload()
    payload["start_at"] = (now - timedelta(hours=1)).isoformat()
    payload["end_at"] = (now + timedelta(hours=2)).isoformat()

    api_client.force_authenticate(user=admin_user)
    response = api_client.post(EVENTS_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "start_at" in response.data


@pytest.mark.django_db
def test_patch_cannot_change_event_status(api_client, admin_user):
    event = _create_event(admin_user)
    detail_url = f"{EVENTS_URL}{event.id}/"

    api_client.force_authenticate(user=admin_user)
    response = api_client.patch(
        detail_url,
        {"status": Event.Status.CLOSED},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    event.refresh_from_db()
    assert event.status == Event.Status.OPEN


@pytest.mark.django_db
def test_event_list_pagination(api_client, admin_user):
    now = timezone.now()
    for idx in range(12):
        Event.objects.create(
            title=f"Tadbir {idx}",
            description="Tavsif",
            event_type=Event.EventType.SEMINAR,
            location="Toshkent",
            start_at=now + timedelta(days=idx + 1),
            end_at=now + timedelta(days=idx + 1, hours=2),
            created_by=admin_user,
        )

    page1 = api_client.get(EVENTS_URL)
    assert page1.status_code == status.HTTP_200_OK
    assert page1.data["count"] == 12
    assert len(page1.data["results"]) == 10

    page2 = api_client.get(f"{EVENTS_URL}?page=2")
    assert page2.status_code == status.HTTP_200_OK
    assert len(page2.data["results"]) == 2


@pytest.mark.django_db
def test_event_list_filters_search_and_ordering(api_client, admin_user):
    now = timezone.now()
    past_event = Event.objects.create(
        title="Python asoslari",
        description="Eski seminar",
        event_type=Event.EventType.SEMINAR,
        location="Toshkent",
        start_at=now - timedelta(days=2),
        end_at=now - timedelta(days=2) + timedelta(hours=2),
        status=Event.Status.CLOSED,
        created_by=admin_user,
    )
    future_drf = Event.objects.create(
        title="Django REST",
        description="API yaratish",
        event_type=Event.EventType.MASTERCLASS,
        location="IT Park",
        start_at=now + timedelta(days=2),
        end_at=now + timedelta(days=2, hours=2),
        created_by=admin_user,
    )
    future_ai = Event.objects.create(
        title="FastAPI",
        description="Django bilan solishtirish",
        event_type=Event.EventType.TRAINING,
        location="IT Park",
        start_at=now + timedelta(days=5),
        end_at=now + timedelta(days=5, hours=2),
        created_by=admin_user,
    )

    resp = api_client.get(f"{EVENTS_URL}?upcoming=true&search=django&ordering=-start_at")
    assert resp.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in resp.data["results"]]
    assert ids == [future_ai.id, future_drf.id]

    closed_resp = api_client.get(f"{EVENTS_URL}?status=closed&event_type=seminar")
    assert [item["id"] for item in closed_resp.data["results"]] == [past_event.id]


@pytest.mark.django_db
def test_event_computed_fields(api_client, user, admin_user):
    now = timezone.now()
    limited = Event.objects.create(
        title="Cheklangan",
        description="Tavsif",
        event_type=Event.EventType.SEMINAR,
        location="Toshkent",
        start_at=now + timedelta(days=1),
        end_at=now + timedelta(days=1, hours=2),
        capacity=10,
        created_by=admin_user,
    )
    unlimited = Event.objects.create(
        title="Cheklanmagan",
        description="Tavsif",
        event_type=Event.EventType.TRAINING,
        location="Toshkent",
        start_at=now + timedelta(days=2),
        end_at=now + timedelta(days=2, hours=2),
        capacity=None,
        created_by=admin_user,
    )
    Registration.objects.create(user=user, event=limited, status=Registration.Status.ACTIVE)
    Registration.objects.create(
        user=admin_user, event=limited, status=Registration.Status.CANCELLED
    )

    guest_detail = api_client.get(f"{EVENTS_URL}{limited.id}/")
    assert guest_detail.data["registered_count"] == 1
    assert guest_detail.data["available_seats"] == 9
    assert guest_detail.data["is_registered"] is False

    api_client.force_authenticate(user=user)
    user_detail = api_client.get(f"{EVENTS_URL}{limited.id}/")
    assert user_detail.data["is_registered"] is True

    unlimited_detail = api_client.get(f"{EVENTS_URL}{unlimited.id}/")
    assert unlimited_detail.data["available_seats"] is None
    assert unlimited_detail.data["is_registered"] is False


@pytest.mark.django_db
def test_event_list_no_n_plus_one_queries(api_client, user, admin_user, django_assert_num_queries):
    now = timezone.now()
    for idx in range(2):
        ev = Event.objects.create(
            title=f"Event {idx}",
            description="Tavsif",
            event_type=Event.EventType.SEMINAR,
            location="Toshkent",
            start_at=now + timedelta(days=idx + 1),
            end_at=now + timedelta(days=idx + 1, hours=2),
            capacity=20,
            created_by=admin_user,
        )
        Registration.objects.create(user=user, event=ev, status=Registration.Status.ACTIVE)

    api_client.force_authenticate(user=user)
    with django_assert_num_queries(2):
        resp_2 = api_client.get(EVENTS_URL)
        assert len(resp_2.data["results"]) == 2

    for idx in range(2, 8):
        ev = Event.objects.create(
            title=f"Event {idx}",
            description="Tavsif",
            event_type=Event.EventType.SEMINAR,
            location="Toshkent",
            start_at=now + timedelta(days=idx + 1),
            end_at=now + timedelta(days=idx + 1, hours=2),
            capacity=20,
            created_by=admin_user,
        )
        Registration.objects.create(user=user, event=ev, status=Registration.Status.ACTIVE)

    with django_assert_num_queries(2):
        resp_8 = api_client.get(EVENTS_URL)
        assert len(resp_8.data["results"]) == 8

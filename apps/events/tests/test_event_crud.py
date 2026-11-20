import pytest
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.events.models import Event, EventType, EventStatus

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="admin@evently.com",
        password="AdminPass123!",
        role="admin"
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        email="user@evently.com",
        password="UserPass123!",
        role="user"
    )


@pytest.fixture
def sample_event(admin_user):
    now = timezone.now()
    return Event.objects.create(
        title="Django REST Framework Asoslari",
        description="Amaliy master-klass",
        event_type=EventType.SEMINAR,
        location="IT Park, 301-xona",
        start_at=now + timedelta(days=2),
        end_at=now + timedelta(days=2, hours=3),
        capacity=30,
        status=EventStatus.OPEN,
        created_by=admin_user
    )


@pytest.mark.django_db
class TestEventModel:
    def test_event_creation_and_str(self, sample_event):
        assert str(sample_event) == "Django REST Framework Asoslari"
        assert sample_event.event_type == EventType.SEMINAR
        assert sample_event.status == EventStatus.OPEN
        assert sample_event.capacity == 30
        assert sample_event.registered_count == 0
        assert sample_event.available_seats == 30
        assert not sample_event.is_finished

    def test_is_finished_true_for_past_event(self, admin_user):
        past_time = timezone.now() - timedelta(days=1)
        past_event = Event.objects.create(
            title="O'tib ketgan tadbir",
            description="Tugagan",
            event_type=EventType.SEMINAR,
            location="Toshkent",
            start_at=past_time - timedelta(hours=2),
            end_at=past_time,
            created_by=admin_user
        )
        assert past_event.is_finished is True


@pytest.mark.django_db
class TestEventPermissions:
    def test_list_and_detail_events_public_for_unauthenticated(self, api_client, sample_event):
        # List
        url = reverse('events:event-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Detail
        detail_url = reverse('events:event-detail', kwargs={'pk': sample_event.pk})
        response = api_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == sample_event.title

    def test_create_event_unauthenticated_returns_401(self, api_client):
        url = reverse('events:event-list')
        now = timezone.now()
        data = {
            "title": "Anonim Tadbir",
            "description": "Tavsif",
            "event_type": "seminar",
            "location": "Online",
            "start_at": (now + timedelta(days=1)).isoformat(),
            "end_at": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_event_regular_user_returns_403(self, api_client, regular_user):
        api_client.force_authenticate(user=regular_user)
        url = reverse('events:event-list')
        now = timezone.now()
        data = {
            "title": "Oddiy User Tadbiri",
            "description": "Tavsif",
            "event_type": "seminar",
            "location": "Online",
            "start_at": (now + timedelta(days=1)).isoformat(),
            "end_at": (now + timedelta(days=1, hours=2)).isoformat(),
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_event_admin_user_returns_201(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('events:event-list')
        now = timezone.now()
        data = {
            "title": "Yangi Admin Tadbiri",
            "description": "Zo'r tadbir",
            "event_type": "masterclass",
            "location": "Toshkent IT Park",
            "start_at": (now + timedelta(days=3)).isoformat(),
            "end_at": (now + timedelta(days=3, hours=2)).isoformat(),
            "capacity": 25,
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "Yangi Admin Tadbiri"
        assert response.data['created_by'] == admin_user.pk
        assert response.data['status'] == "open"

    def test_delete_event_admin_returns_204(self, api_client, admin_user, sample_event):
        api_client.force_authenticate(user=admin_user)
        url = reverse('events:event-detail', kwargs={'pk': sample_event.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Event.objects.filter(pk=sample_event.pk).exists()

    def test_close_event_action(self, api_client, admin_user, regular_user, sample_event):
        close_url = reverse('events:event-close', kwargs={'pk': sample_event.pk})

        # Regular user 403
        api_client.force_authenticate(user=regular_user)
        res = api_client.post(close_url)
        assert res.status_code == status.HTTP_403_FORBIDDEN

        # Admin user 200
        api_client.force_authenticate(user=admin_user)
        res = api_client.post(close_url)
        assert res.status_code == status.HTTP_200_OK
        sample_event.refresh_from_db()
        assert sample_event.status == EventStatus.CLOSED


@pytest.mark.django_db
class TestEventValidations:
    def test_br8_start_at_cannot_be_past(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('events:event-list')
        now = timezone.now()
        data = {
            "title": "O'tgan sana tadbiri",
            "description": "Tavsif",
            "event_type": "seminar",
            "location": "Online",
            "start_at": (now - timedelta(days=1)).isoformat(),
            "end_at": (now + timedelta(days=1)).isoformat(),
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "start_at" in response.data

    def test_br7_end_at_must_be_after_start_at(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('events:event-list')
        now = timezone.now()
        data = {
            "title": "Xato vaqtli tadbir",
            "description": "Tavsif",
            "event_type": "seminar",
            "location": "Online",
            "start_at": (now + timedelta(days=2)).isoformat(),
            "end_at": (now + timedelta(days=1)).isoformat(),
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "end_at" in response.data

    def test_readonly_status_and_created_by_cannot_be_patched(self, api_client, admin_user, regular_user, sample_event):
        api_client.force_authenticate(user=admin_user)
        url = reverse('events:event-detail', kwargs={'pk': sample_event.pk})
        data = {
            "status": "closed",
            "created_by": regular_user.pk
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        sample_event.refresh_from_db()
        # To'g'ridan-to'g'ri patch orqali o'zgarmasligi kerak
        assert sample_event.status == EventStatus.OPEN
        assert sample_event.created_by == admin_user


@pytest.mark.django_db
class TestEventFiltersAndSearch:
    def test_filter_by_event_type_and_status(self, api_client, admin_user):
        now = timezone.now()
        Event.objects.create(
            title="Seminar 1",
            description="Tavsif 1",
            event_type=EventType.SEMINAR,
            location="A",
            start_at=now + timedelta(days=1),
            end_at=now + timedelta(days=1, hours=2),
            status=EventStatus.OPEN,
            created_by=admin_user
        )
        Event.objects.create(
            title="Masterclass 1",
            description="Tavsif 2",
            event_type=EventType.MASTERCLASS,
            location="B",
            start_at=now + timedelta(days=2),
            end_at=now + timedelta(days=2, hours=2),
            status=EventStatus.CLOSED,
            created_by=admin_user
        )

        url = reverse('events:event-list')

        # Filter by event_type=seminar
        res = api_client.get(f"{url}?event_type=seminar")
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] == 1
        assert res.data['results'][0]['title'] == "Seminar 1"

        # Search by title
        res = api_client.get(f"{url}?search=Masterclass")
        assert res.status_code == status.HTTP_200_OK
        assert res.data['count'] == 1
        assert res.data['results'][0]['title'] == "Masterclass 1"

import pytest
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.test import APIClient
from rest_framework import status
from apps.events.models import Event, EventType, EventStatus, Registration, RegistrationStatus

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="admin_reg@evently.com",
        password="AdminPass123!",
        role="admin"
    )


@pytest.fixture
def regular_user1():
    return User.objects.create_user(
        email="user1_reg@evently.com",
        password="UserPass123!",
        first_name="Ali",
        last_name="Valiyev",
        phone_number="+998901112233"
    )


@pytest.fixture
def regular_user2():
    return User.objects.create_user(
        email="user2_reg@evently.com",
        password="UserPass123!",
        first_name="Gani",
        last_name="Soliyev",
        phone_number="+998902223344"
    )


@pytest.fixture
def open_event(admin_user):
    now = timezone.now()
    return Event.objects.create(
        title="Django REST Practice",
        description="Amaliy dars",
        event_type=EventType.SEMINAR,
        location="Toshkent IT Park",
        start_at=now + timedelta(days=5),
        end_at=now + timedelta(days=5, hours=3),
        capacity=2,  # Kichik capacity testlar uchun
        status=EventStatus.OPEN,
        created_by=admin_user
    )


@pytest.mark.django_db
class TestRegistrationBusinessRules:
    def test_registration_success(self, api_client, regular_user1, open_event):
        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-register', kwargs={'pk': open_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'active'
        assert response.data['event_id'] == open_event.pk
        open_event.refresh_from_db()
        assert open_event.registered_count == 1
        assert open_event.available_seats == 1

    def test_registration_unauthenticated_returns_401(self, api_client, open_event):
        url = reverse('events:event-register', kwargs={'pk': open_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_registration_br1_duplicate_fails(self, api_client, regular_user1, open_event):
        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-register', kwargs={'pk': open_event.pk})
        # 1-marta muvaffaqiyatli
        res1 = api_client.post(url)
        assert res1.status_code == status.HTTP_201_CREATED

        # 2-marta allaqachon yozilgan
        res2 = api_client.post(url)
        assert res2.status_code == status.HTTP_400_BAD_REQUEST
        assert res2.data['code'] == 'already_registered'

    def test_registration_br2_capacity_full_fails(self, api_client, regular_user1, regular_user2, admin_user, open_event):
        # 2 ta joy to'ldiriladi
        Registration.objects.create(user=regular_user1, event=open_event, status=RegistrationStatus.ACTIVE)
        Registration.objects.create(user=regular_user2, event=open_event, status=RegistrationStatus.ACTIVE)

        # 3-foydalanuvchi yozila olmaydi
        user3 = User.objects.create_user(email="user3@evently.com", password="PassWord123!")
        api_client.force_authenticate(user=user3)
        url = reverse('events:event-register', kwargs={'pk': open_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 'event_full'

    def test_registration_br3_event_started_fails(self, api_client, regular_user1, admin_user):
        past_time = timezone.now() - timedelta(hours=1)
        started_event = Event.objects.create(
            title="Boshlangan tadbir",
            description="Tavsif",
            event_type=EventType.SEMINAR,
            location="Online",
            start_at=past_time,
            end_at=past_time + timedelta(hours=2),
            capacity=10,
            status=EventStatus.OPEN,
            created_by=admin_user
        )
        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-register', kwargs={'pk': started_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 'event_started'

    def test_registration_br5_event_closed_fails(self, api_client, regular_user1, open_event):
        open_event.status = EventStatus.CLOSED
        open_event.save(update_fields=['status'])

        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-register', kwargs={'pk': open_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 'event_closed'

    def test_unregister_success(self, api_client, regular_user1, open_event):
        Registration.objects.create(user=regular_user1, event=open_event, status=RegistrationStatus.ACTIVE)
        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-unregister', kwargs={'pk': open_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        reg = Registration.objects.get(user=regular_user1, event=open_event)
        assert reg.status == RegistrationStatus.CANCELLED
        assert reg.cancelled_at is not None
        open_event.refresh_from_db()
        assert open_event.registered_count == 0

    def test_unregister_br6_after_start_fails(self, api_client, regular_user1, admin_user):
        now = timezone.now()
        started_event = Event.objects.create(
            title="Boshlangan tadbir",
            description="Tavsif",
            event_type=EventType.SEMINAR,
            location="Zal",
            start_at=now - timedelta(minutes=10),
            end_at=now + timedelta(hours=1),
            created_by=admin_user
        )
        Registration.objects.create(user=regular_user1, event=started_event, status=RegistrationStatus.ACTIVE)
        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-unregister', kwargs={'pk': started_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 'event_started'

    def test_unregister_not_registered_fails(self, api_client, regular_user1, open_event):
        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-unregister', kwargs={'pk': open_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 'not_registered'

    def test_re_registration_after_cancellation(self, api_client, regular_user1, open_event):
        # Chiqib ketgan yozuv mavjud
        reg = Registration.objects.create(
            user=regular_user1,
            event=open_event,
            status=RegistrationStatus.CANCELLED,
            cancelled_at=timezone.now()
        )
        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:event-register', kwargs={'pk': open_event.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED

        # Yangi yozuv yaratilmasligi, eskisini active qilish
        assert Registration.objects.filter(user=regular_user1, event=open_event).count() == 1
        reg.refresh_from_db()
        assert reg.status == RegistrationStatus.ACTIVE
        assert reg.cancelled_at is None

    def test_my_registrations_br10(self, api_client, regular_user1, regular_user2, open_event):
        # user1 bitta tadbirga yozilgan
        Registration.objects.create(user=regular_user1, event=open_event, status=RegistrationStatus.ACTIVE)
        # user2 ikkinchi tadbirga yozilgan
        now = timezone.now()
        event2 = Event.objects.create(
            title="Boshqa tadbir",
            description="Tavsif",
            event_type=EventType.TRAINING,
            location="B",
            start_at=now + timedelta(days=3),
            end_at=now + timedelta(days=3, hours=2),
            created_by=open_event.created_by
        )
        Registration.objects.create(user=regular_user2, event=event2, status=RegistrationStatus.ACTIVE)

        api_client.force_authenticate(user=regular_user1)
        url = reverse('events:my-registrations')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Faqat user1 o'z tadbirini ko'radi (count == 1)
        assert response.data['count'] == 1
        assert response.data['results'][0]['event']['title'] == open_event.title

    def test_participants_list_permissions(self, api_client, regular_user1, regular_user2, admin_user, open_event):
        Registration.objects.create(user=regular_user1, event=open_event, status=RegistrationStatus.ACTIVE)
        url = reverse('events:event-participants', kwargs={'pk': open_event.pk})

        # Unauthenticated -> 401
        res_anon = api_client.get(url)
        assert res_anon.status_code == status.HTTP_401_UNAUTHORIZED

        # Regular user -> 403
        api_client.force_authenticate(user=regular_user2)
        res_user = api_client.get(url)
        assert res_user.status_code == status.HTTP_403_FORBIDDEN

        # Admin -> 200 OK
        api_client.force_authenticate(user=admin_user)
        res_admin = api_client.get(url)
        assert res_admin.status_code == status.HTTP_200_OK
        assert len(res_admin.data) == 1
        assert res_admin.data[0]['email'] == regular_user1.email
        assert res_admin.data[0]['full_name'] == "Ali Valiyev"

    def test_unique_constraint_at_db_level(self, regular_user1, open_event):
        Registration.objects.create(user=regular_user1, event=open_event, status=RegistrationStatus.ACTIVE)
        with pytest.raises(IntegrityError):
            Registration.objects.create(user=regular_user1, event=open_event, status=RegistrationStatus.ACTIVE)

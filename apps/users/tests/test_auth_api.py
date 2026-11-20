import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_test_user():
    def _create(email="user@example.com", password="StrongPassword123!", role="user"):
        return User.objects.create_user(email=email, password=password, role=role)
    return _create


@pytest.mark.django_db
class TestAuthAPI:
    def test_register_user_success(self, api_client):
        url = reverse('auth:register')
        data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "first_name": "Aziz",
            "last_name": "Karimov",
            "phone_number": "+998901234567"
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == "newuser@example.com"
        assert response.data['role'] == "user"
        assert "password" not in response.data

    def test_register_existing_email_fails(self, api_client, create_test_user):
        create_test_user(email="existing@example.com")
        url = reverse('auth:register')
        data = {
            "email": "existing@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_cannot_set_admin_role(self, api_client):
        url = reverse('auth:register')
        data = {
            "email": "hacker@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "role": "admin"
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        # Foydalanuvchi baribir 'user' bo'lib ro'yxatdan o'tishi shart
        assert response.data['role'] == "user"
        user = User.objects.get(email="hacker@example.com")
        assert user.role == "user"

    def test_login_success(self, api_client, create_test_user):
        create_test_user(email="login@example.com", password="Password123!")
        url = reverse('auth:login')
        data = {
            "email": "login@example.com",
            "password": "Password123!"
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_get_me_unauthorized(self, api_client):
        url = reverse('auth:me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_authorized(self, api_client, create_test_user):
        user = create_test_user(email="me@example.com")
        api_client.force_authenticate(user=user)
        url = reverse('auth:me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == "me@example.com"

    def test_patch_me_cannot_change_role(self, api_client, create_test_user):
        user = create_test_user(email="me2@example.com")
        api_client.force_authenticate(user=user)
        url = reverse('auth:me')
        data = {
            "first_name": "UpdatedName",
            "role": "admin"
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == "UpdatedName"
        assert response.data['role'] == "user"
        user.refresh_from_db()
        assert user.role == "user"

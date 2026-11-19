import pytest
from rest_framework import status

from apps.users.models import User

REGISTER_URL = "/api/v1/auth/register/"
LOGIN_URL = "/api/v1/auth/login/"
ME_URL = "/api/v1/auth/me/"


@pytest.mark.django_db
def test_register_success(api_client):
    payload = {
        "email": "aziz@example.com",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "first_name": "Aziz",
        "last_name": "Karimov",
        "phone_number": "+998901234567",
    }
    response = api_client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["email"] == "aziz@example.com"
    assert response.data["role"] == User.Role.USER
    assert "password" not in response.data

    created_user = User.objects.get(email="aziz@example.com")
    assert created_user.check_password("StrongPass123!")


@pytest.mark.django_db
def test_register_duplicate_email(api_client, user):
    payload = {
        "email": user.email,
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "first_name": "Dup",
        "last_name": "User",
    }
    response = api_client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_login_success_and_wrong_password(api_client, user):
    ok_response = api_client.post(
        LOGIN_URL,
        {"email": user.email, "password": "StrongPassword123!"},
        format="json",
    )
    assert ok_response.status_code == status.HTTP_200_OK
    assert "access" in ok_response.data
    assert "refresh" in ok_response.data

    bad_response = api_client.post(
        LOGIN_URL,
        {"email": user.email, "password": "WrongPassword123!"},
        format="json",
    )
    assert bad_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_register_and_patch_me_ignore_admin_role(api_client, user):
    reg_payload = {
        "email": "hacker@example.com",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "first_name": "Hacker",
        "last_name": "Test",
        "role": "admin",
    }
    reg_response = api_client.post(REGISTER_URL, reg_payload, format="json")
    assert reg_response.status_code == status.HTTP_201_CREATED
    assert reg_response.data["role"] == User.Role.USER
    assert User.objects.get(email="hacker@example.com").role == User.Role.USER

    api_client.force_authenticate(user=user)
    patch_response = api_client.patch(
        ME_URL,
        {"first_name": "Updated", "role": "admin"},
        format="json",
    )
    assert patch_response.status_code == status.HTTP_200_OK
    assert patch_response.data["role"] == User.Role.USER
    user.refresh_from_db()
    assert user.role == User.Role.USER
    assert user.first_name == "Updated"

import pytest
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        email="user@example.com",
        password="StrongPassword123!",
        first_name="Test",
        last_name="User",
        phone_number="+998901234567",
        role=User.Role.USER,
    )


@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_user(
        email="admin@example.com",
        password="StrongPassword123!",
        first_name="Admin",
        last_name="User",
        phone_number="+998907654321",
        role="admin",
    )

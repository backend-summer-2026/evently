import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_successful(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "testuser@example.com"
        assert user.check_password("StrongPassword123!")
        assert user.role == "user"
        assert not user.is_staff
        assert not user.is_superuser
        assert not user.is_admin

    def test_create_user_without_email_raises_error(self):
        with pytest.raises(ValueError, match="Email manzili ko'rsatilishi shart."):
            User.objects.create_user(email="", password="SomePassword123!")

    def test_create_superuser_successful(self):
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPassword123!",
        )
        assert admin_user.email == "admin@example.com"
        assert admin_user.is_staff
        assert admin_user.is_superuser
        assert admin_user.role == "admin"
        assert admin_user.is_admin

    def test_user_str_representation(self):
        user = User.objects.create_user(email="aziz@example.com", password="PassWord123!")
        assert str(user) == "aziz@example.com"

    def test_user_full_name_property(self):
        user = User.objects.create_user(
            email="aziz@example.com",
            password="PassWord123!",
            first_name="Aziz",
            last_name="Karimov"
        )
        assert user.full_name == "Aziz Karimov"

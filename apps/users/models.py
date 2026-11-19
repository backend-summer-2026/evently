from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """Username maydoni olib tashlangani sababli foydalanuvchilarni email orqali yaratish."""

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("Foydalanuvchi uchun email kiritilishi shart.")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", User.Role.USER)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        # Superuser tizimda avtomatik ravishda admin roliga ega bo'lishi kerak
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo'lishi shart.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo'lishi shart.")

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    # Login email orqali bo'lgani uchun standart username ustuni kerak emas
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_link_token = models.CharField(max_length=64, null=True, blank=True, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.email

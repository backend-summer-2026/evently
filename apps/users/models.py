from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.users.managers import UserManager


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    USER = 'user', 'Foydalanuvchi'


class User(AbstractUser):
    """
    Custom User model using email as primary identifier.
    """
    username = None
    email = models.EmailField(
        verbose_name="Elektron pochta",
        unique=True,
        error_messages={
            'unique': "Ushbu email bilan ro'yxatdan o'tilgan.",
        }
    )
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Ism")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Familiya")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Telefon raqami")
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name="Rol"
    )
    telegram_chat_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="Telegram Chat ID"
    )
    telegram_link_token = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True,
        verbose_name="Telegram Bog'lash Tokeni"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def full_name(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.email

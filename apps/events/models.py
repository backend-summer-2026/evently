from django.conf import settings
from django.db import models


class Event(models.Model):
    class EventType(models.TextChoices):
        SEMINAR = "seminar", "Seminar"
        MASTERCLASS = "masterclass", "Masterclass"
        TRAINING = "training", "Training"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    location = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    # capacity null bo'lsa qatnashuvchilar soni cheklanmagan hisoblanadi (BR-2)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_at"]

    def __str__(self) -> str:
        return self.title


class Registration(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # BR-1: Bir foydalanuvchi bir tadbirga faqat bir marta yozila oladi
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_registration",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.event} ({self.status})"

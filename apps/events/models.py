from django.db import models
from django.conf import settings
from django.utils import timezone


class EventType(models.TextChoices):
    SEMINAR = 'seminar', 'Seminar'
    MASTERCLASS = 'masterclass', 'Master-klass'
    TRAINING = 'training', 'Trening'


class EventStatus(models.TextChoices):
    OPEN = 'open', 'Ochiq'
    CLOSED = 'closed', 'Yopiq'


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif")
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.SEMINAR,
        verbose_name="Tadbir turi"
    )
    location = models.CharField(max_length=255, verbose_name="Manzil / Joy")
    start_at = models.DateTimeField(verbose_name="Boshlanish vaqti")
    end_at = models.DateTimeField(verbose_name="Tugash vaqti")
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Sig'im / Joylar soni"
    )
    status = models.CharField(
        max_length=10,
        choices=EventStatus.choices,
        default=EventStatus.OPEN,
        verbose_name="Holat"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_events',
        verbose_name="Yaratuvchi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")

    class Meta:
        verbose_name = "Tadbir"
        verbose_name_plural = "Tadbirlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def registered_count(self) -> int:
        if hasattr(self, '_registered_count'):
            return self._registered_count
        try:
            if hasattr(self, 'registrations'):
                return self.registrations.filter(status='active').count()
        except Exception:
            pass
        return 0

    @property
    def available_seats(self):
        if self.capacity is None:
            return None
        return max(0, self.capacity - self.registered_count)

    @property
    def is_finished(self) -> bool:
        if self.end_at:
            return self.end_at < timezone.now()
        return False

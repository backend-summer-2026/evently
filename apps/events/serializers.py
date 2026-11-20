from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.events.models import Event


class BaseEventSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True, default=0)
    available_seats = serializers.SerializerMethodField()
    is_finished = serializers.SerializerMethodField()
    is_registered = serializers.BooleanField(read_only=True, default=False)

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_available_seats(self, obj: Event) -> int | None:
        # BR-2: capacity null bo'lsa bo'sh joylar soni ham cheklanmagan (null) bo'ladi
        if obj.capacity is None:
            return None
        registered_count = getattr(obj, "registered_count", 0)
        return max(obj.capacity - registered_count, 0)

    @extend_schema_field(serializers.BooleanField())
    def get_is_finished(self, obj: Event) -> bool:
        return bool(obj.end_at < timezone.now())


class EventListSerializer(BaseEventSerializer):
    """Ro'yxat endpointi uchun qisqa serializer."""

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "event_type",
            "location",
            "start_at",
            "capacity",
            "registered_count",
            "available_seats",
            "status",
            "is_finished",
            "is_registered",
        )
        read_only_fields = fields


class EventDetailSerializer(BaseEventSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "event_type",
            "location",
            "start_at",
            "end_at",
            "capacity",
            "registered_count",
            "available_seats",
            "status",
            "is_finished",
            "is_registered",
            "created_by",
            "created_at",
            "updated_at",
        )
        # status alohida close endpointi orqali o'zgaradi, created_by esa view'da avtomatik yoziladi
        read_only_fields = (
            "id",
            "registered_count",
            "available_seats",
            "status",
            "is_finished",
            "is_registered",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate_capacity(self, value: int | None) -> int | None:
        # PositiveIntegerField 0 ni ham qabul qilgani uchun kamida 1 ta joy bo'lishini tekshiramiz
        if value is not None and value < 1:
            raise serializers.ValidationError(
                "Joylar soni kamida 1 bo'lishi yoki cheklanmagan (null) qoldirilishi kerak."
            )
        return value

    def validate(self, attrs: dict) -> dict:
        # BR-8: Yangi tadbir o'tgan sanaga yaratilmasligi shart
        if self.instance is None and "start_at" in attrs:
            if attrs["start_at"] <= timezone.now():
                raise serializers.ValidationError(
                    {"start_at": "Yangi tadbirning boshlanish vaqti kelajakda bo'lishi kerak."}
                )

        # BR-7: Create va partial update (PATCH) da ham end_at > start_at bo'lishi shart
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if start_at is not None and end_at is not None and end_at <= start_at:
            raise serializers.ValidationError(
                {"end_at": "Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak."}
            )

        return attrs

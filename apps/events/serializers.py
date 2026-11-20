from django.utils import timezone
from rest_framework import serializers
from config.exceptions import BusinessLogicError
from apps.events.models import Event, EventType, EventStatus


class EventListSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'event_type',
            'location',
            'start_at',
            'capacity',
            'available_seats',
            'status',
            'is_registered',
        ]

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        if hasattr(obj, 'registrations'):
            return obj.registrations.filter(user=request.user, status='active').exists()
        return False


class EventDetailSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'event_type',
            'location',
            'start_at',
            'end_at',
            'capacity',
            'registered_count',
            'available_seats',
            'status',
            'is_finished',
            'is_registered',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_by', 'created_at', 'updated_at']

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        if hasattr(obj, 'registrations'):
            return obj.registrations.filter(user=request.user, status='active').exists()
        return False


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'event_type',
            'location',
            'start_at',
            'end_at',
            'capacity',
            'status',
            'created_by',
            'registered_count',
            'available_seats',
            'is_finished',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'created_by',
            'registered_count',
            'available_seats',
            'is_finished',
            'created_at',
            'updated_at',
        ]

    def validate_capacity(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Sig'im kamida 1 bo'lishi kerak.")
        return value

    def validate(self, attrs):
        start_at = attrs.get('start_at')
        end_at = attrs.get('end_at')

        if self.instance:
            if start_at is None:
                start_at = self.instance.start_at
            if end_at is None:
                end_at = self.instance.end_at

        # BR-8: Yangi yaratishda start_at kelajakda bo'lishi kerak
        if not self.instance:
            if start_at and start_at <= timezone.now():
                raise serializers.ValidationError({
                    'start_at': "Tadbir boshlanish vaqti kelajakda bo‘lishi kerak."
                })

        # BR-7: end_at > start_at
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({
                'end_at': "Tugash vaqti boshlanish vaqtidan keyin bo‘lishi kerak."
            })

        # BR-9: capacity < registered_count bo'lmasligi kerak
        if self.instance and 'capacity' in attrs:
            new_capacity = attrs['capacity']
            if new_capacity is not None and new_capacity < self.instance.registered_count:
                raise BusinessLogicError(
                    detail="Joylar soni hozirgi qatnashuvchilar sonidan kam bo‘lishi mumkin emas.",
                    code="capacity_too_low"
                )

        return attrs

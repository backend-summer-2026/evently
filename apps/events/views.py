from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.users.permissions import IsAdmin, IsAdminOrReadOnly
from apps.events.models import Event, EventStatus, Registration, RegistrationStatus
from apps.events.filters import EventFilter
from apps.events.services import (
    register_for_event,
    unregister_from_event,
    close_event,
)
from apps.events.serializers import (
    EventListSerializer,
    EventDetailSerializer,
    EventCreateUpdateSerializer,
    ParticipantSerializer,
    MyRegistrationSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Tadbirlar ro'yxati",
        description="Barcha tadbirlar ro'yxatini olish (pagination, filter va qidiruv bilan).",
        responses={200: EventListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Tadbir haqida batafsil",
        description="Alohida tadbir ma'lumotlarini olish.",
        responses={200: EventDetailSerializer}
    ),
    create=extend_schema(
        summary="Yangi tadbir yaratish",
        description="Faqat admin uchun tadbir yaratish imkoniyati.",
        request=EventCreateUpdateSerializer,
        responses={201: EventDetailSerializer}
    ),
    update=extend_schema(
        summary="Tadbirni to'liq yangilash",
        description="Faqat admin uchun tadbirni yangilash.",
        request=EventCreateUpdateSerializer,
        responses={200: EventDetailSerializer}
    ),
    partial_update=extend_schema(
        summary="Tadbirni qisman yangilash",
        description="Faqat admin uchun tadbir parametrlarini o'zgartirish.",
        request=EventCreateUpdateSerializer,
        responses={200: EventDetailSerializer}
    ),
    destroy=extend_schema(
        summary="Tadbirni o'chirish",
        description="Faqat admin uchun tadbirni o'chirish.",
        responses={204: None}
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('created_by')
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = EventFilter
    search_fields = ['title', 'description']
    ordering_fields = ['start_at', 'created_at']
    ordering = ['start_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = self.perform_create(serializer)
        output_serializer = EventDetailSerializer(event, context=self.get_serializer_context())
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        output_serializer = EventDetailSerializer(event, context=self.get_serializer_context())
        return Response(output_serializer.data)

    @extend_schema(
        summary="Tadbirni yopish",
        description="Faqat admin uchun: tadbir statusini 'closed' holatiga o'tkazish.",
        request=None,
        responses={200: EventDetailSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def close(self, request, pk=None):
        event = self.get_object()
        event = close_event(event_id=event.id)
        output_serializer = EventDetailSerializer(event, context=self.get_serializer_context())
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Tadbirga yozilish",
        description="Kirgan foydalanuvchi tadbirga ro'yxatdan o'tadi (BR-1, BR-2, BR-3, BR-5).",
        request=None,
        responses={201: {"type": "object", "properties": {"detail": {"type": "string"}, "registration_id": {"type": "integer"}}}}
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        reg = register_for_event(request.user, event)
        return Response(
            {
                "detail": "Tadbirga muvaffaqiyatli yozildingiz.",
                "registration_id": reg.id,
                "event_id": event.id,
                "event_title": event.title,
                "status": reg.status,
            },
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Tadbirdan chiqish",
        description="Foydalanuvchi tadbirdan ro'yxatdan chiqadi (BR-6).",
        request=None,
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}, "event_id": {"type": "integer"}}}}
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unregister(self, request, pk=None):
        event = self.get_object()
        unregister_from_event(request.user, event)
        return Response(
            {
                "detail": "Tadbirdan muvaffaqiyatli chiqdingiz.",
                "event_id": event.id,
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Tadbir qatnashuvchilari ro'yxati",
        description="Faqat admin uchun: tadbirning barcha faol qatnashuvchilarini ko'rish.",
        responses={200: ParticipantSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAdmin])
    def participants(self, request, pk=None):
        event = self.get_object()
        regs = event.registrations.filter(status=RegistrationStatus.ACTIVE).select_related('user')
        serializer = ParticipantSerializer(regs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Mening ro'yxatdan o'tgan tadbirlarim",
    description="Joriy login qilgan foydalanuvchi o'zi yozilgan tadbirlar ro'yxatini oladi (?status=active yoki ?status=cancelled).",
    responses={200: MyRegistrationSerializer(many=True)}
)
class MyRegistrationsView(generics.ListAPIView):
    serializer_class = MyRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.request.user.registrations.select_related('event')

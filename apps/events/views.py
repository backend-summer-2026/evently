from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.users.permissions import IsAdmin, IsAdminOrReadOnly
from apps.events.models import Event, EventStatus
from apps.events.filters import EventFilter
from apps.events.serializers import (
    EventListSerializer,
    EventDetailSerializer,
    EventCreateUpdateSerializer,
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
        event.status = EventStatus.CLOSED
        event.save(update_fields=['status', 'updated_at'])
        output_serializer = EventDetailSerializer(event, context=self.get_serializer_context())
        return Response(output_serializer.data, status=status.HTTP_200_OK)

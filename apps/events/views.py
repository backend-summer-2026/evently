from django.db.models import BooleanField, Count, Exists, OuterRef, Q, QuerySet, Value
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import filters, serializers, viewsets

from apps.events.filters import EventFilter
from apps.events.models import Event, Registration
from apps.events.serializers import EventDetailSerializer, EventListSerializer
from apps.users.permissions import IsAdminOrReadOnly

EVENT_CREATE_EXAMPLE = OpenApiExample(
    "Tadbir yaratish misoli",
    value={
        "title": "Django REST Framework asoslari",
        "description": "API yaratish bo'yicha amaliy master-klass. Noutbuk olib keling.",
        "event_type": "masterclass",
        "location": "IT Park, 3-qavat, 301-xona",
        "start_at": "2026-12-05T14:00:00+05:00",
        "end_at": "2026-12-05T17:00:00+05:00",
        "capacity": 30,
    },
    request_only=True,
)

EVENT_LIST_PARAMETERS = [
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description="Sahifa raqami (sahifada 10 ta tadbir).",
    ),
    OpenApiParameter(
        name="event_type",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        enum=[choice[0] for choice in Event.EventType.choices],
        description="Tadbir turi bo'yicha filter (`seminar`, `masterclass`, `training`).",
    ),
    OpenApiParameter(
        name="status",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        enum=[choice[0] for choice in Event.Status.choices],
        description="Tadbir holati bo'yicha filter (`open`, `closed`).",
    ),
    OpenApiParameter(
        name="upcoming",
        type=OpenApiTypes.BOOL,
        location=OpenApiParameter.QUERY,
        description="`true` bo'lsa faqat hali boshlanmagan (`start_at > hozir`) tadbirlar.",
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description="`title` va `description` bo'yicha qidiruv.",
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        enum=["start_at", "-start_at", "created_at", "-created_at"],
        description="Saralash maydoni (`start_at`, `-start_at`, `created_at`).",
    ),
]


@extend_schema_view(
    list=extend_schema(
        tags=["events"],
        summary="Tadbirlar ro'yxati",
        description="Barcha tadbirlar ro'yxatini sahifalangan (10 tadan) holda qaytaradi.",
        parameters=EVENT_LIST_PARAMETERS,
        responses={200: EventListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["events"],
        summary="Tadbir haqida batafsil ma'lumot",
        description="ID bo'yicha tadbirning barcha ma'lumotlarini qaytaradi.",
        responses={
            200: EventDetailSerializer,
            404: OpenApiResponse(description="Tadbir topilmadi"),
        },
    ),
    create=extend_schema(
        tags=["events"],
        summary="Yangi tadbir yaratish (faqat Admin)",
        description=(
            "Faqat `role='admin'` foydalanuvchilar yangi tadbir yarata oladi. "
            "`start_at` kelajakda va `end_at > start_at` bo'lishi shart."
        ),
        examples=[EVENT_CREATE_EXAMPLE],
        responses={
            201: EventDetailSerializer,
            400: OpenApiResponse(description="Validatsiya xatosi"),
            401: OpenApiResponse(description="Avtorizatsiya talab qilinadi"),
            403: OpenApiResponse(description="Faqat admin uchun ruxsat etilgan"),
        },
    ),
    partial_update=extend_schema(
        tags=["events"],
        summary="Tadbirni qisman tahrirlash (faqat Admin)",
        description="Faqat admin tadbir ma'lumotlarini `PATCH` orqali yangilay oladi.",
        responses={
            200: EventDetailSerializer,
            400: OpenApiResponse(description="Validatsiya xatosi"),
            401: OpenApiResponse(description="Avtorizatsiya talab qilinadi"),
            403: OpenApiResponse(description="Faqat admin uchun ruxsat etilgan"),
            404: OpenApiResponse(description="Tadbir topilmadi"),
        },
    ),
    destroy=extend_schema(
        tags=["events"],
        summary="Tadbirni o'chirish (faqat Admin)",
        description="Faqat admin tadbirni o'chira oladi.",
        responses={
            204: OpenApiResponse(description="Tadbir muvaffaqiyatli o'chirildi"),
            401: OpenApiResponse(description="Avtorizatsiya talab qilinadi"),
            403: OpenApiResponse(description="Faqat admin uchun ruxsat etilgan"),
            404: OpenApiResponse(description="Tadbir topilmadi"),
        },
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = EventFilter
    search_fields = ("title", "description")
    ordering_fields = ("start_at", "created_at")
    ordering = ("start_at",)
    # PUT o'rniga faqat qisman yangilash (PATCH) ruxsat etiladi
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self) -> QuerySet[Event]:
        user = self.request.user
        if user and user.is_authenticated:
            is_registered_expr = Exists(
                Registration.objects.filter(
                    event=OuterRef("pk"),
                    user=user,
                    status=Registration.Status.ACTIVE,
                )
            )
        else:
            is_registered_expr = Value(False, output_field=BooleanField())

        # N+1 muammosi bo'lmasligi uchun hisoblanadigan maydonlar bitta SQL so'rovda olinadi
        return Event.objects.annotate(
            registered_count=Count(
                "registrations",
                filter=Q(registrations__status=Registration.Status.ACTIVE),
            ),
            is_registered=is_registered_expr,
        ).order_by("start_at")

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        if self.action == "list":
            return EventListSerializer
        return EventDetailSerializer

    def perform_create(self, serializer: EventDetailSerializer) -> None:
        serializer.save(created_by=self.request.user)

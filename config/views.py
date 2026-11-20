from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import connection
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema


class HealthCheckView(APIView):
    """
    Server va ma'lumotlar bazasi holatini tekshiruvchi Health Check endpoint.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Server holatini tekshirish (Health Check)",
        description="Backend API va ma'lumotlar bazasi ulanishini tekshiradi.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "database": {"type": "string", "example": "connected"},
                    "timezone": {"type": "string", "example": "Asia/Tashkent"},
                    "timestamp": {"type": "string", "example": "2026-11-20T20:25:00+05:00"},
                }
            }
        }
    )
    def get(self, request, *args, **kwargs):
        db_status = "connected"
        try:
            connection.ensure_connection()
        except Exception as e:
            db_status = f"unreachable: {str(e)}"
            return Response(
                {
                    "status": "unhealthy",
                    "database": db_status,
                    "timestamp": timezone.now().isoformat(),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response({
            "status": "healthy",
            "database": db_status,
            "timezone": settings.TIME_ZONE,
            "timestamp": timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)

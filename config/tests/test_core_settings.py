import pytest
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from config.exceptions import BusinessLogicError, custom_exception_handler
from config.pagination import CustomPagination


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestCoreSettingsAndHealth:
    def test_health_check_endpoint_success(self, api_client):
        url = reverse('health-check')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert response.data['database'] == 'connected'
        assert response.data['timezone'] == settings.TIME_ZONE
        assert 'timestamp' in response.data

    def test_custom_exception_handler_business_error(self):
        exc = BusinessLogicError(detail="Maxsus xatolik yuz berdi.", code="custom_error_code")
        response = custom_exception_handler(exc, context={})
        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail'] == "Maxsus xatolik yuz berdi."
        assert response.data['code'] == "custom_error_code"

    def test_custom_pagination_structure(self):
        from rest_framework.request import Request
        factory = APIRequestFactory()
        wsgi_request = factory.get('/dummy/?page=1&page_size=5')
        request = Request(wsgi_request)
        paginator = CustomPagination()

        items = list(range(1, 13))  # 12 ta element
        page = paginator.paginate_queryset(items, request)
        response = paginator.get_paginated_response(page)

        assert response.status_code == 200
        assert response.data['count'] == 12
        assert response.data['total_pages'] == 3
        assert response.data['current_page'] == 1
        assert response.data['page_size'] == 5
        assert len(response.data['results']) == 5
        assert response.data['next'] is not None
        assert response.data['previous'] is None

    def test_cors_settings_configured(self):
        assert hasattr(settings, 'CORS_ALLOWED_ORIGINS')
        assert isinstance(settings.CORS_ALLOWED_ORIGINS, list)
        assert 'corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE

    def test_logging_directory_created(self):
        assert settings.LOGS_DIR.exists()

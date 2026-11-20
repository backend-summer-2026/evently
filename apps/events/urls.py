from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.events.views import EventViewSet, MyRegistrationsView

app_name = 'events'

router = DefaultRouter()
router.register('events', EventViewSet, basename='event')

urlpatterns = [
    path('me/registrations/', MyRegistrationsView.as_view(), name='my-registrations'),
] + router.urls

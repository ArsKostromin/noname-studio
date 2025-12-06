from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ScheduleViewSet, my_schedule

router = DefaultRouter()
router.register("schedule", ScheduleViewSet)

urlpatterns = [
    path("my-schedule/", my_schedule, name="my-schedule"),
] + router.urls

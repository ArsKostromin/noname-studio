from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import GradeViewSet, my_grades

router = DefaultRouter()
router.register("grades", GradeViewSet)

urlpatterns = [
    path("my-grades/", my_grades, name="my-grades"),
] + router.urls

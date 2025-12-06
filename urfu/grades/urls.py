from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import GradeViewSet, TestResultViewSet, my_grades

router = DefaultRouter()
router.register("grades", GradeViewSet)
router.register("tests", TestResultViewSet)

urlpatterns = [
    path("my-grades/", my_grades, name="my-grades"),
] + router.urls

from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import TeacherViewSet, GroupViewSet, StudentViewSet, SubjectViewSet
from .auth import login_view, refresh_view, logout_view

router = DefaultRouter()
router.register("teachers", TeacherViewSet)
router.register("groups", GroupViewSet)
router.register("students", StudentViewSet)
router.register("subjects", SubjectViewSet)

urlpatterns = [
    path("auth/login/", login_view, name="login"),
    path("auth/refresh/", refresh_view, name="refresh"),
    path("auth/logout/", logout_view, name="logout"),
] + router.urls

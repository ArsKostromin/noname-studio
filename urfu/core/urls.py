from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import TeacherViewSet, GroupViewSet, StudentViewSet, SubjectViewSet
from .auth import login_view, accept_token

router = DefaultRouter()
router.register("teachers", TeacherViewSet)
router.register("groups", GroupViewSet)
router.register("students", StudentViewSet)
router.register("subjects", SubjectViewSet)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("accept-token/", accept_token, name="accept-token"),
] + router.urls

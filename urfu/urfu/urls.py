from django.urls import path, include

urlpatterns = [
    path("api/core/", include("core.urls")),
    path("api/schedule/", include("schedule.urls")),
    path("api/grades/", include("grades.urls")),
]

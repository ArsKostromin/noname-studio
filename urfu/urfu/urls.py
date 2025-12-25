from django.urls import path, include
from django.contrib import admin


from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path("api/core/", include("core.urls")),
    path("api/schedule/", include("schedule.urls")),
    path("api/grades/", include("grades.urls")),
    
    # Swagger/OpenAPI documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

from django.urls import include, path
from .views import HealthCheckView

app_name = "v1"

urlpatterns = [
    path(
        "health/",
        HealthCheckView.as_view(),
        name="health",
    ),

    path(
        "auth/",
        include("apps.identity.urls"),
    ),
    path(
        "",
        include("apps.facilities.urls"),
    ),
    path(
        "",
        include("apps.patients.urls"),
    ),
    path(
        "",
        include("apps.encounters.urls"),
    ),
    path(
        "",
        include("apps.investigations.urls"),
    ),
    path(
        "",
        include("apps.laboratory.urls"),
    ),
]
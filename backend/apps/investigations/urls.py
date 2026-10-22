from rest_framework.routers import DefaultRouter

from .views import InvestigationViewSet


router = DefaultRouter()

router.register(
    "investigations",
    InvestigationViewSet,
    basename="investigation",
)

urlpatterns = router.urls
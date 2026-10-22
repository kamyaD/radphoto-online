from rest_framework.routers import DefaultRouter

from .views import (
    LaboratoryOrderItemViewSet,
    LaboratoryOrderViewSet,
    LaboratoryPanelTestViewSet,
    LaboratoryPanelViewSet,
    LaboratorySpecimenViewSet,
    LaboratoryTestViewSet,
)


router = DefaultRouter()

router.register(
    "laboratory/tests",
    LaboratoryTestViewSet,
    basename="laboratory-test",
)

router.register(
    "laboratory/orders",
    LaboratoryOrderViewSet,
    basename="laboratory-order",
)
router.register(
    "laboratory/panels",
    LaboratoryPanelViewSet,
    basename="laboratory-panel",
)

router.register(
    "laboratory/panel-tests",
    LaboratoryPanelTestViewSet,
    basename="laboratory-panel-test",
)

router.register(
    "laboratory/order-items",
    LaboratoryOrderItemViewSet,
    basename="laboratory-order-item",
)

router.register(
    "laboratory/specimens",
    LaboratorySpecimenViewSet,
    basename="laboratory-specimen",
)


urlpatterns = router.urls
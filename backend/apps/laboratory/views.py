from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    LaboratoryOrder,
    LaboratoryOrderItem,
    LaboratoryPanel,
    LaboratoryPanelTest,
    LaboratorySpecimen,
    LaboratoryTest,
    LaboratoryItemResult
)
from .permissions import (
    CanAccessLaboratory,
    CanAccessLaboratoryOrderItem,
    CanAccessLaboratorySpecimen,
    CanProcessLaboratory,
)
from .serializers import (
    LaboratoryItemResultSerializer,
    LaboratoryOrderItemSerializer,
    LaboratoryOrderSerializer,
    LaboratoryPanelSerializer,
    LaboratoryPanelTestSerializer,
    LaboratorySpecimenSerializer,
    LaboratoryTestSerializer,
    LaboratoryResultSerializer
)
from .services import (
    collect_specimen,
    create_laboratory_order,
    start_processing,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Laboratory"]
    ),
    create=extend_schema(
        tags=["Laboratory"]
    ),
    retrieve=extend_schema(
        tags=["Laboratory"]
    ),
    partial_update=extend_schema(
        tags=["Laboratory"]
    ),
)
class LaboratoryTestViewSet(
    viewsets.ModelViewSet
):
    queryset = LaboratoryTest.objects.all()

    serializer_class = LaboratoryTestSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]


@extend_schema_view(
    list=extend_schema(
        tags=["Laboratory"]
    ),
    create=extend_schema(
        tags=["Laboratory"]
    ),
    retrieve=extend_schema(
        tags=["Laboratory"]
    ),
    partial_update=extend_schema(
        tags=["Laboratory"]
    ),
)
class LaboratoryOrderViewSet(
    viewsets.ModelViewSet
):
    serializer_class = LaboratoryOrderSerializer

    permission_classes = [
        IsAuthenticated,
        CanAccessLaboratory,
    ]

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            LaboratoryOrder.objects
            .select_related(
                "investigation",
                "investigation__facility",
                "investigation__patient",
                "test",
                "collected_by",
                "processed_by",
                "verified_by",
            )
        )

        if user.is_staff:
            return queryset

        return queryset.filter(
            investigation__facility__memberships__user=user,
            investigation__facility__memberships__is_active=True,
        ).distinct()

    @extend_schema(
        tags=["Laboratory"],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="queue",
        permission_classes=[
            IsAuthenticated,
            CanProcessLaboratory,
        ],
    )
    def queue(self, request):
        queryset = self.get_queryset().filter(
            status__in=[
                LaboratoryOrder.STATUS_PENDING,
                LaboratoryOrder.STATUS_SPECIMEN_COLLECTED,
                LaboratoryOrder.STATUS_IN_PROGRESS,
            ]
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data
        )

    @extend_schema(
        tags=["Laboratory"],
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="collect-specimen",
        permission_classes=[
            IsAuthenticated,
            CanProcessLaboratory,
        ],
    )
    def collect_specimen_action(
        self,
        request,
        pk=None,
    ):
        laboratory_order = self.get_object()

        laboratory_order = collect_specimen(
            laboratory_order,
            request.user,
        )

        return Response(
            self.get_serializer(
                laboratory_order
            ).data
        )

    @extend_schema(
        tags=["Laboratory"],
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="start",
        permission_classes=[
            IsAuthenticated,
            CanProcessLaboratory,
        ],
    )
    def start_action(
        self,
        request,
        pk=None,
    ):
        laboratory_order = self.get_object()

        laboratory_order = start_processing(
            laboratory_order,
            request.user,
        )

        return Response(
            self.get_serializer(
                laboratory_order
            ).data
        )

    @extend_schema(
    tags=["Laboratory"],
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="result",
        permission_classes=[
            IsAuthenticated,
            CanProcessLaboratory,
        ],
    )
    def result(
        self,
        request,
        pk=None,
    ):
        from .services import enter_result

        laboratory_order = self.get_object()

        laboratory_result = enter_result(
            laboratory_order=laboratory_order,
            user=request.user,
            result_value=request.data.get(
                "result_value",
                "",
            ),
            unit=request.data.get(
                "unit",
                "",
            ),
            reference_range=request.data.get(
                "reference_range",
                "",
            ),
            flag=request.data.get(
                "flag",
                "NORMAL",
            ),
            interpretation=request.data.get(
                "interpretation",
                "",
            ),
        )

        return Response(
            LaboratoryResultSerializer(
                laboratory_result
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
    tags=["Laboratory"],
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="verify",
        permission_classes=[
            IsAuthenticated,
            CanProcessLaboratory,
        ],
    )
    def verify(
        self,
        request,
        pk=None,
    ):
        from .services import verify_result

        laboratory_order = self.get_object()

        laboratory_order = verify_result(
            laboratory_order,
            request.user,
        )

        return Response(
            self.get_serializer(
                laboratory_order
            ).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="specimen",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def specimen(self, request, pk=None):
        from .services import create_specimen

        laboratory_order = self.get_object()

        specimen_type = request.data.get(
            "specimen_type",
            "",
        )

        specimen = create_specimen(
            laboratory_order=laboratory_order,
            specimen_type=specimen_type,
            user=request.user,
        )

        return Response(
            LaboratorySpecimenSerializer(specimen).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="add-panel",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def add_panel(self, request, pk=None):
        from .services import add_panel_to_order

        laboratory_order = self.get_object()

        panel_id = request.data.get("panel")

        if not panel_id:
            return Response(
                {
                    "detail": "panel is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            panel = LaboratoryPanel.objects.get(
                pk=panel_id,
                is_active=True,
            )
        except LaboratoryPanel.DoesNotExist:
            return Response(
                {
                    "detail": "Laboratory panel not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        items = add_panel_to_order(
            laboratory_order,
            panel,
        )

        return Response(
            LaboratoryOrderItemSerializer(
                items,
                many=True,
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="add-test",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def add_test(self, request, pk=None):
        from .services import add_test_to_order

        laboratory_order = self.get_object()

        test_id = request.data.get("test")

        if not test_id:
            return Response(
                {
                    "detail": "test is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            test = LaboratoryTest.objects.get(
                pk=test_id,
                is_active=True,
            )
        except LaboratoryTest.DoesNotExist:
            return Response(
                {
                    "detail": "Laboratory test not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        item = add_test_to_order(
            laboratory_order,
            test,
        )

        return Response(
            LaboratoryOrderItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(tags=["Laboratory Panels"]),
    create=extend_schema(tags=["Laboratory Panels"]),
    retrieve=extend_schema(tags=["Laboratory Panels"]),
    partial_update=extend_schema(tags=["Laboratory Panels"]),
)
class LaboratoryPanelViewSet(viewsets.ModelViewSet):
    queryset = LaboratoryPanel.objects.prefetch_related(
        "panel_tests__test"
    )

    serializer_class = LaboratoryPanelSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]


class LaboratoryPanelTestViewSet(viewsets.ModelViewSet):
    queryset = LaboratoryPanelTest.objects.select_related(
        "panel",
        "test",
    )

    serializer_class = LaboratoryPanelTestSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

@extend_schema_view(
    list=extend_schema(tags=["Laboratory Specimens"]),
    retrieve=extend_schema(tags=["Laboratory Specimens"]),
)
class LaboratorySpecimenViewSet(viewsets.ModelViewSet
):
    serializer_class = LaboratorySpecimenSerializer

    permission_classes = [
        IsAuthenticated,
        CanAccessLaboratorySpecimen,
    ]
    ttp_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            LaboratorySpecimen.objects
            .select_related(
                "laboratory_order",
                "laboratory_order__investigation",
                "laboratory_order__investigation__facility",
                "laboratory_order__investigation__patient",
                "collected_by",
                "received_by",
            )
        )

        if user.is_staff:
            return queryset

        return queryset.filter(
            laboratory_order__investigation__facility__memberships__user=user,
            laboratory_order__investigation__facility__memberships__is_active=True,
        ).distinct()


@extend_schema_view(
    list=extend_schema(tags=["Laboratory Tests"]),
    retrieve=extend_schema(tags=["Laboratory Tests"]),
)
class LaboratoryOrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LaboratoryOrderItemSerializer

    permission_classes = [
        IsAuthenticated,
        CanAccessLaboratoryOrderItem,
    ]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            LaboratoryOrderItem.objects
            .select_related(
                "laboratory_order",
                "laboratory_order__investigation",
                "laboratory_order__investigation__facility",
                "laboratory_order__investigation__patient",
                "test",
                "specimen",
                "verified_by",
            )
        )

        if user.is_staff:
            return queryset

        return queryset.filter(
            laboratory_order__investigation__facility__memberships__user=user,
            laboratory_order__investigation__facility__memberships__is_active=True,
        ).distinct()

    @action(
    detail=True,
    methods=["post"],
    url_path="start",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def start(self, request, pk=None):
        item = self.get_object()

        if item.status != LaboratoryOrderItem.STATUS_PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending laboratory tests "
                        "can be started."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.status = LaboratoryOrderItem.STATUS_IN_PROGRESS
        item.started_at = timezone.now()

        item.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

        return Response(
            self.get_serializer(item).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="result",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def result(self, request, pk=None):
        from .services import enter_item_result

        item = self.get_object()

        result = enter_item_result(
            order_item=item,
            user=request.user,
            result_value=request.data.get(
                "result_value",
                "",
            ),
            unit=request.data.get(
                "unit",
                "",
            ),
            reference_range=request.data.get(
                "reference_range",
                "",
            ),
            flag=request.data.get(
                "flag",
                LaboratoryItemResult.FLAG_NORMAL,
            ),
            interpretation=request.data.get(
                "interpretation",
                "",
            ),
        )

        return Response(
            LaboratoryItemResultSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="verify",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def verify(self, request, pk=None):
        from .services import verify_item_result

        item = self.get_object()

        item = verify_item_result(
            item,
            request.user,
        )

        return Response(
            self.get_serializer(item).data
        )


    @action(
    detail=True,
    methods=["post"],
    url_path="receive",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def receive(self, request, pk=None):
        from .services import receive_specimen

        specimen = self.get_object()

        specimen = receive_specimen(
            specimen,
            request.user,
        )

        return Response(
            self.get_serializer(specimen).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="reject",
    permission_classes=[
        IsAuthenticated,
        CanProcessLaboratory,
    ],
    )
    def reject(self, request, pk=None):
        from .services import reject_specimen

        specimen = self.get_object()

        specimen = reject_specimen(
            specimen,
            request.data.get(
                "reason",
                "",
            ),
        )

        return Response(
            self.get_serializer(specimen).data
        )



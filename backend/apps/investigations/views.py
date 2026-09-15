from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.db.models import Case, IntegerField, Value, When

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Investigation
from .permissions import (CanAccessInvestigation, CanProcessInvestigation)
from .serializers import InvestigationSerializer
from .services import (
    assign_investigation,
    cancel_investigation,
    complete_investigation,
    generate_investigation_number,
    mark_reported,
    queue_investigation,
    start_investigation,
)


@extend_schema_view(
    list=extend_schema(tags=["Investigations"]),
    create=extend_schema(tags=["Investigations"]),
    retrieve=extend_schema(tags=["Investigations"]),
    partial_update=extend_schema(tags=["Investigations"]),
)
class InvestigationViewSet(viewsets.ModelViewSet):

    serializer_class = InvestigationSerializer

    permission_classes = [
        IsAuthenticated,
        CanAccessInvestigation,
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

        if user.is_staff:
            return (
                Investigation.objects
                .select_related(
                    "facility",
                    "patient",
                    "encounter",
                    "ordered_by",
                )
                .all()
            )

        return (
            Investigation.objects
            .select_related(
                "facility",
                "patient",
                "encounter",
                "ordered_by",
            )
            .filter(
                facility__memberships__user=user,
                facility__memberships__is_active=True,
            )
            .distinct()
        )

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user

        facility = serializer.validated_data["facility"]
        patient = serializer.validated_data["patient"]
        encounter = serializer.validated_data["encounter"]

        if not user.is_staff:
            has_access = (
                user.facility_memberships
                .filter(
                    facility=facility,
                    is_active=True,
                )
                .exists()
            )

            if not has_access:
                raise PermissionDenied(
                    "You do not have access to this facility."
                )

        if patient.facility_id != facility.id:
            raise PermissionDenied(
                "Patient does not belong to this facility."
            )

        if encounter.facility_id != facility.id:
            raise PermissionDenied(
                "Encounter does not belong to this facility."
            )

        if encounter.patient_id != patient.id:
            raise PermissionDenied(
                "Encounter does not belong to this patient."
            )

        investigation_number = (
            generate_investigation_number()
        )

        serializer.save(
            investigation_number=investigation_number,
            ordered_by=user,
        )

    def perform_update(self, serializer):
        instance = self.get_object()

        new_status = serializer.validated_data.get(
            "status",
            instance.status,
        )

        if (
            new_status == Investigation.STATUS_COMPLETED
            and instance.status != Investigation.STATUS_COMPLETED
        ):
            serializer.save(
                completed_at=timezone.now()
            )
            return

        if (
            new_status == Investigation.STATUS_CANCELLED
            and instance.status != Investigation.STATUS_CANCELLED
        ):
            serializer.save(
                cancelled_at=timezone.now()
            )
            return

        serializer.save()

    @extend_schema(
        tags=["Investigations"],
        description=(
            "Search investigations by investigation number, "
            "patient number, patient name, or investigation name."
        ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="search",
    )
    def search(self, request):
        query = request.query_params.get(
            "q",
            "",
        ).strip()

        if not query:
            return Response(
                {
                    "detail": (
                        "Search query parameter 'q' "
                        "is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(
            Q(
                investigation_number__icontains=query
            )
            | Q(
                patient__patient_number__icontains=query
            )
            | Q(
                patient__first_name__icontains=query
            )
            | Q(
                patient__middle_name__icontains=query
            )
            | Q(
                patient__last_name__icontains=query
            )
            | Q(
                investigation_name__icontains=query
            )
        )

        serializer = self.get_serializer(
            queryset[:50],
            many=True,
        )

        return Response(serializer.data)

    @extend_schema(
        tags=["Investigations"],
        description=(
            "Return all investigations belonging "
            "to a specific patient."
        ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="patient/(?P<patient_id>[^/.]+)",
    )
    def patient_investigations(
        self,
        request,
        patient_id=None,
    ):
        queryset = self.get_queryset().filter(
            patient_id=patient_id
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    @extend_schema(
    tags=["Investigations"],
    description=(
        "Return investigations waiting for processing "
        "by department."
    ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="queue",
    )
    def queue(self, request):
        department = request.query_params.get(
            "department"
        )

        status_filter = request.query_params.get(
            "status",
            Investigation.STATUS_QUEUED,
        )

        queryset = self.get_queryset()

        if department:
            queryset = queryset.filter(
                department=department
            )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter
            )

        queryset = queryset.annotate(
            priority_order=Case(
                When(
                    priority=Investigation.PRIORITY_STAT,
                    then=Value(1),
                ),
                When(
                    priority=Investigation.PRIORITY_URGENT,
                    then=Value(2),
                ),
                When(
                    priority=Investigation.PRIORITY_ROUTINE,
                    then=Value(3),
                ),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by(
            "priority_order",
            "ordered_at",
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)
    @action(
    detail=True,
    methods=["post"],
    url_path="queue",
    permission_classes=[
        IsAuthenticated,
        CanProcessInvestigation,
    ],
    )
    def queue(self, request, pk=None):
        investigation = self.get_object()

        investigation = queue_investigation(
            investigation
        )

        return Response(
            self.get_serializer(investigation).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="assign",
    permission_classes=[
        IsAuthenticated,
        CanProcessInvestigation,
    ],
    )
    def assign(self, request, pk=None):
        investigation = self.get_object()

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {
                    "detail": "user_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(
                id=user_id,
                is_active=True,
            )
        except User.DoesNotExist:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.facility_memberships.filter(
            facility=investigation.facility,
            is_active=True,
        ).exists() and not user.is_staff:
            return Response(
                {
                    "detail": (
                        "The selected user does not belong "
                        "to this facility."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        investigation = assign_investigation(
            investigation,
            user,
        )

        return Response(
            self.get_serializer(investigation).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="start",
    permission_classes=[
        IsAuthenticated,
        CanProcessInvestigation,
    ],
    )
    def start(self, request, pk=None):
        investigation = self.get_object()

        investigation = start_investigation(
            investigation,
            request.user,
        )

        return Response(
            self.get_serializer(investigation).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="complete",
    permission_classes=[
        IsAuthenticated,
        CanProcessInvestigation,
    ],
    )
    def complete(self, request, pk=None):
        investigation = self.get_object()

        investigation = complete_investigation(
            investigation,
            request.user,
        )

        return Response(
            self.get_serializer(investigation).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="report",
    permission_classes=[
        IsAuthenticated,
        CanProcessInvestigation,
    ],
    )
    def report(self, request, pk=None):
        investigation = self.get_object()

        investigation = mark_reported(
            investigation
        )

        return Response(
            self.get_serializer(investigation).data
        )

    @action(
    detail=True,
    methods=["post"],
    url_path="cancel",
    permission_classes=[
        IsAuthenticated,
        CanProcessInvestigation,
    ],
    )
    def cancel(self, request, pk=None):
        investigation = self.get_object()

        reason = request.data.get(
            "reason",
            "",
        ).strip()

        if not reason:
            return Response(
                {
                    "detail": "Cancellation reason is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        investigation = cancel_investigation(
            investigation,
            reason,
        )

        return Response(
            self.get_serializer(investigation).data
        )
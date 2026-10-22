from django.db import transaction
from django.db.models import Q
from django.utils import timezone


from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Encounter
from .permissions import CanAccessEncounter
from .serializers import EncounterSerializer
from .services import generate_encounter_number


@extend_schema_view(
    list=extend_schema(
        tags=["Encounters"],
    ),
    create=extend_schema(
        tags=["Encounters"],
    ),
    retrieve=extend_schema(
        tags=["Encounters"],
    ),
    partial_update=extend_schema(
        tags=["Encounters"],
    ),
)
class EncounterViewSet(viewsets.ModelViewSet):
    serializer_class = EncounterSerializer

    permission_classes = [
        IsAuthenticated,
        CanAccessEncounter,
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
                Encounter.objects
                .select_related(
                    "facility",
                    "patient",
                    "attending_user",
                )
                .all()
            )

        return (
            Encounter.objects
            .select_related(
                "facility",
                "patient",
                "attending_user",
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

        encounter_number = generate_encounter_number()

        serializer.save(
            encounter_number=encounter_number,
        )

    def perform_update(self, serializer):
        instance = self.get_object()

        new_status = serializer.validated_data.get(
            "status",
            instance.status,
        )

        if (
            new_status == Encounter.STATUS_COMPLETED
            and instance.status != Encounter.STATUS_COMPLETED
        ):
            serializer.save(
                completed_at=timezone.now(),
            )
            return

        serializer.save()

    @extend_schema(
        tags=["Encounters"],
        description=(
            "Search encounters by encounter number, "
            "patient number, patient name, or clinical text."
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
            Q(encounter_number__icontains=query)
            | Q(patient__patient_number__icontains=query)
            | Q(patient__first_name__icontains=query)
            | Q(patient__middle_name__icontains=query)
            | Q(patient__last_name__icontains=query)
            | Q(chief_complaint__icontains=query)
        )

        serializer = self.get_serializer(
            queryset[:50],
            many=True,
        )

        return Response(serializer.data)

    @extend_schema(
        tags=["Encounters"],
        description=(
            "Return all encounters belonging to a specific patient."
        ),
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="patient/(?P<patient_id>[^/.]+)",
    )
    def patient_encounters(
        self,
        request,
        patient_id=None,
    ):
        queryset = self.get_queryset().filter(
            patient_id=patient_id,
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)
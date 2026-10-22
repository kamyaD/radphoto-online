from django.db import transaction
from django.db.models import Q

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Patient
from .permissions import CanAccessPatient
from .serializers import PatientSerializer
from .services import generate_patient_number


@extend_schema_view(
    list=extend_schema(
        tags=["Patients"],
    ),
    create=extend_schema(
        tags=["Patients"],
    ),
    retrieve=extend_schema(
        tags=["Patients"],
    ),
    partial_update=extend_schema(
        tags=["Patients"],
    ),
    destroy=extend_schema(
        tags=["Patients"],
    ),
)
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [
        IsAuthenticated,
        CanAccessPatient,
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
            return Patient.objects.select_related(
                "facility"
            ).all()

        return (
            Patient.objects
            .select_related("facility")
            .filter(
                is_active=True,
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
            has_access = user.facility_memberships.filter(
                facility=facility,
                is_active=True,
            ).exists()

            if not has_access:
                

                raise PermissionDenied(
                    "You do not have access to this facility."
                )

        patient_number = generate_patient_number()

        serializer.save(
            patient_number=patient_number,
        )

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()

        patient.is_active = False
        patient.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "Patient has been deactivated."
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Patients"],
        description=(
            "Search patients by patient number, "
            "name, phone number, or email."
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
            Q(patient_number__icontains=query)
            | Q(first_name__icontains=query)
            | Q(middle_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(email__icontains=query)
        )

        serializer = self.get_serializer(
            queryset[:50],
            many=True,
        )

        return Response(serializer.data)
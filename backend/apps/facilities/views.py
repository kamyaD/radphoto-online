from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from apps.identity.permissions import (
    IsSystemAdminOrFacilityAdmin,
)

from .models import Facility
from .serializers import FacilitySerializer
from .services import generate_facility_number
from .permissions import CanManageFacility


class FacilityViewSet(viewsets.ModelViewSet):
    """
    Facility management API.

    System administrators:
        - create facilities
        - view all facilities
        - update facilities
        - deactivate facilities

    Facility administrators:
        - view their own facility
        - update their own facility
        - view their facility members
    """

    serializer_class = FacilitySerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Facility.objects.all()

        return Facility.objects.filter(
            is_active=True,
            memberships__user=user,
            memberships__is_active=True,
        ).distinct()

    def get_permissions(self):
        if self.action == "create":
            return [
                IsAuthenticated(),
                IsSystemAdminOrFacilityAdmin(),
            ]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAuthenticated(),
                CanManageFacility(),
            ]

        return [
            IsAuthenticated(),
        ]

    @transaction.atomic
    def perform_create(self, serializer):
        facility_number = (
            generate_facility_number()
        )

        serializer.save(
            facility_number=facility_number
        )

    def destroy(self, request, *args, **kwargs):
        """
        Soft-delete/deactivate a facility.

        Healthcare records must remain historically
        available, therefore the facility is not
        physically deleted.
        """

        facility = self.get_object()

        facility.is_active = False
        facility.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Facility has been deactivated."
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="members",
    )
    def members(self, request, pk=None):
        facility = self.get_object()

        memberships = (
            facility.memberships
            .filter(is_active=True)
            .select_related("user")
        )

        data = [
            {
                "id": membership.id,
                "user_id": membership.user.id,
                "username": membership.user.username,
                "email": membership.user.email,
                "role": membership.role,
                "is_active": membership.is_active,
            }
            for membership in memberships
        ]

        return Response(data)
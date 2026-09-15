from rest_framework.permissions import BasePermission


class CanAccessInvestigation(BasePermission):
    message = "You do not have access to this investigation."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return request.user.facility_memberships.filter(
            facility=obj.facility,
            is_active=True,
        ).exists()


class CanProcessInvestigation(BasePermission):
    message = "You do not have permission to process this investigation."

    PROCESSING_ROLES = [
        "LAB_TECHNICIAN",
        "RADTECH",
        "RADIOGRAPHER",
        "ECHOCARDIOGRAPHER",
        "CARDIOLOGIST",
        "PATHOLOGIST",
        "FACILITY_ADMIN",
    ]

    def has_permission(self, request, view):
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        if request.user.is_staff:
            return True

        return request.user.facility_memberships.filter(
            role__in=self.PROCESSING_ROLES,
            is_active=True,
        ).exists()

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return request.user.facility_memberships.filter(
            facility=obj.facility,
            role__in=self.PROCESSING_ROLES,
            is_active=True,
        ).exists()
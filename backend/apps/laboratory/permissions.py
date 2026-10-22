from rest_framework.permissions import BasePermission


class CanAccessLaboratory(BasePermission):
    message = (
        "You do not have access to this laboratory record."
    )

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if request.user.is_staff:
            return True

        return request.user.facility_memberships.filter(
            facility=obj.investigation.facility,
            is_active=True,
        ).exists()


class CanProcessLaboratory(BasePermission):
    message = (
        "Laboratory processing permission required."
    )

    ALLOWED_ROLES = [
        "LAB_TECHNICIAN",
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
            role__in=self.ALLOWED_ROLES,
            is_active=True,
        ).exists()

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if request.user.is_staff:
            return True

        return request.user.facility_memberships.filter(
            facility=obj.investigation.facility,
            role__in=self.ALLOWED_ROLES,
            is_active=True,
        ).exists()


class CanAccessLaboratoryOrderItem(BasePermission):
    message = "You do not have access to this laboratory test."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return request.user.facility_memberships.filter(
            facility=obj.laboratory_order.investigation.facility,
            is_active=True,
        ).exists()

class CanAccessLaboratorySpecimen(BasePermission):
    message = "You do not have access to this specimen."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return request.user.facility_memberships.filter(
            facility=obj.laboratory_order.investigation.facility,
            is_active=True,
        ).exists()
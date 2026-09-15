from rest_framework.permissions import BasePermission


class CanAccessPatient(BasePermission):
    message = "You do not have access to this patient."

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
            facility=obj.facility,
            is_active=True,
        ).exists()
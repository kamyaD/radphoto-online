from rest_framework.permissions import BasePermission


class CanManageFacility(BasePermission):
    """
    System administrators can manage all facilities.

    Facility administrators can manage only facilities
    where they have an active FACILITY_ADMIN membership.
    """

    message = (
        "You do not have permission to manage "
        "this facility."
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

        return (
            request.user
            .facility_memberships
            .filter(
                facility=obj,
                role="FACILITY_ADMIN",
                is_active=True,
            )
            .exists()
        )
from rest_framework.permissions import BasePermission


class HasFacilityAccess(BasePermission):
    """
    Ensures the authenticated user has an active
    membership with the requested facility.

    The view should provide:

        facility_id = ...
    """

    message = "You do not have access to this facility."

    def has_permission(self, request, view):
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        facility_id = getattr(
            view,
            "facility_id",
            None,
        )

        if facility_id is None:
            return False

        return request.user.facility_memberships.filter(
            facility_id=facility_id,
            is_active=True,
        ).exists()
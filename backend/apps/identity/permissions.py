from rest_framework.permissions import BasePermission


class IsSystemAdmin(BasePermission):
    """
    Allows access to Django staff/system administrators.
    """

    message = "System administrator access required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsFacilityAdmin(BasePermission):
    """
    Allows facility administrators.
    """

    message = "Facility administrator access required."

    def has_permission(self, request, view):
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        return request.user.facility_memberships.filter(
            role="FACILITY_ADMIN",
            is_active=True,
        ).exists()


class HasFacilityRole(BasePermission):
    """
    Checks whether the authenticated user has one
    of the roles required by the view.

    The view must define:

        required_roles = [
            "DOCTOR",
            "RADIOLOGIST",
        ]
    """

    message = "You do not have the required facility role."

    def has_permission(self, request, view):
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        required_roles = getattr(
            view,
            "required_roles",
            [],
        )

        if not required_roles:
            return False

        return request.user.facility_memberships.filter(
            role__in=required_roles,
            is_active=True,
        ).exists()
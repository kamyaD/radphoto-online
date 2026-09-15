from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.facilities.models import Facility


class User(AbstractUser):
    """
    Custom RadPhoto Online user.

    Authentication is handled by Django.
    Authorization will be handled through roles,
    permissions, and facility membership.
    """

    email = models.EmailField(
        unique=True,
        blank=False,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.username


class FacilityMembership(models.Model):
    """
    Connects a user to a facility and defines
    the user's role within that facility.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="facility_memberships",
    )

    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    role = models.CharField(
        max_length=50,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "facility", "role"],
                name="unique_user_facility_role",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.facility.name} - "
            f"{self.role}"
        )
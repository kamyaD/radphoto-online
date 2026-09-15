from django.db import models


class Facility(models.Model):
    name = models.CharField(max_length=255)

    facility_number = models.CharField(
        max_length=50,
        unique=True,
    )

    registration_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    address = models.TextField(
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
        return f"{self.facility_number} - {self.name}"
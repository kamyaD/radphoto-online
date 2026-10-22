from django.db import models

from apps.facilities.models import Facility


class Patient(models.Model):
    SEX_MALE = "MALE"
    SEX_FEMALE = "FEMALE"
    SEX_OTHER = "OTHER"
    SEX_UNKNOWN = "UNKNOWN"

    SEX_CHOICES = [
        (SEX_MALE, "Male"),
        (SEX_FEMALE, "Female"),
        (SEX_OTHER, "Other"),
        (SEX_UNKNOWN, "Unknown"),
    ]

    patient_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
    )

    facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        related_name="patients",
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(
        max_length=100,
        blank=True,
    )
    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    sex = models.CharField(
        max_length=20,
        choices=SEX_CHOICES,
        default=SEX_UNKNOWN,
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

    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
    )

    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    registration_date = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["-registration_date"]
        indexes = [
            models.Index(
                fields=["facility", "patient_number"],
            ),
            models.Index(
                fields=["facility", "last_name", "first_name"],
            ),
            models.Index(
                fields=["facility", "phone_number"],
            ),
        ]

    def __str__(self):
        return f"{self.patient_number} - {self.full_name}"

    @property
    def full_name(self):
        names = [
            self.first_name,
            self.middle_name,
            self.last_name,
        ]

        return " ".join(
            name.strip()
            for name in names
            if name and name.strip()
        )
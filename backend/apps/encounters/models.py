from django.conf import settings
from django.db import models

from apps.facilities.models import Facility
from apps.patients.models import Patient


class Encounter(models.Model):
    TYPE_OUTPATIENT = "OUTPATIENT"
    TYPE_INPATIENT = "INPATIENT"
    TYPE_EMERGENCY = "EMERGENCY"
    TYPE_FOLLOW_UP = "FOLLOW_UP"

    TYPE_CHOICES = [
        (TYPE_OUTPATIENT, "Outpatient"),
        (TYPE_INPATIENT, "Inpatient"),
        (TYPE_EMERGENCY, "Emergency"),
        (TYPE_FOLLOW_UP, "Follow-up"),
    ]

    STATUS_OPEN = "OPEN"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    encounter_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
    )

    facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        related_name="encounters",
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="encounters",
    )

    encounter_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default=TYPE_OUTPATIENT,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )

    attending_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attended_encounters",
        null=True,
        blank=True,
    )

    chief_complaint = models.TextField(
        blank=True,
    )

    clinical_notes = models.TextField(
        blank=True,
    )

    registration_time = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-registration_time"]
        indexes = [
            models.Index(
                fields=["facility", "encounter_number"],
            ),
            models.Index(
                fields=["facility", "patient"],
            ),
            models.Index(
                fields=["facility", "registration_time"],
            ),
            models.Index(
                fields=["patient", "registration_time"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.encounter_number} - "
            f"{self.patient.patient_number}"
        )
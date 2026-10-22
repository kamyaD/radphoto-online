from django.conf import settings
from django.db import models

from apps.encounters.models import Encounter
from apps.facilities.models import Facility
from apps.patients.models import Patient


class Investigation(models.Model):
    # Investigation departments
    DEPARTMENT_LABORATORY = "LABORATORY"
    DEPARTMENT_RADIOLOGY = "RADIOLOGY"
    DEPARTMENT_CARDIOLOGY = "CARDIOLOGY"
    DEPARTMENT_PATHOLOGY = "PATHOLOGY"

    DEPARTMENT_CHOICES = [
        (DEPARTMENT_LABORATORY, "Laboratory"),
        (DEPARTMENT_RADIOLOGY, "Radiology"),
        (DEPARTMENT_CARDIOLOGY, "Cardiology"),
        (DEPARTMENT_PATHOLOGY, "Pathology"),
    ]

    # Investigation types
    TYPE_LABORATORY = "LABORATORY"
    TYPE_RADIOLOGY = "RADIOLOGY"
    TYPE_ECG = "ECG"
    TYPE_ECHOCARDIOGRAPHY = "ECHOCARDIOGRAPHY"
    TYPE_PATHOLOGY = "PATHOLOGY"

    TYPE_CHOICES = [
        (TYPE_LABORATORY, "Laboratory"),
        (TYPE_RADIOLOGY, "Radiology"),
        (TYPE_ECG, "ECG"),
        (TYPE_ECHOCARDIOGRAPHY, "Echocardiography"),
        (TYPE_PATHOLOGY, "Pathology"),
    ]

    # Priority
    PRIORITY_ROUTINE = "ROUTINE"
    PRIORITY_URGENT = "URGENT"
    PRIORITY_STAT = "STAT"

    PRIORITY_CHOICES = [
        (PRIORITY_ROUTINE, "Routine"),
        (PRIORITY_URGENT, "Urgent"),
        (PRIORITY_STAT, "STAT"),
    ]

    # Status
    STATUS_ORDERED = "ORDERED"
    STATUS_QUEUED = "QUEUED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_REPORTED = "REPORTED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_ORDERED, "Ordered"),
        (STATUS_QUEUED, "Queued"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_REPORTED, "Reported"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    investigation_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
    )

    facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        related_name="investigations",
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="investigations",
    )

    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.PROTECT,
        related_name="investigations",
    )

    ordered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ordered_investigations",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_investigations",
        null=True,
        blank=True,
    )

    department = models.CharField(
        max_length=30,
        choices=DEPARTMENT_CHOICES,
    )

    investigation_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
    )

    investigation_name = models.CharField(
        max_length=255,
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_ROUTINE,
    )

    clinical_indication = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ORDERED,
    )

    ordered_at = models.DateTimeField(
        auto_now_add=True,
    )

    queued_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reported_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancellation_reason = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-ordered_at"]
        indexes = [
            models.Index(
                fields=["facility", "investigation_number"]
            ),
            models.Index(
                fields=["facility", "patient"]
            ),
            models.Index(
                fields=["facility", "encounter"]
            ),
            models.Index(
                fields=["facility", "department", "status"]
            ),
            models.Index(
                fields=["facility", "ordered_at"]
            ),
            models.Index(
            fields=[
                "facility",
                "department",
                "status",
                "priority",
            ]
        ),
        ]

    def __str__(self):
        return (
            f"{self.investigation_number} - "
            f"{self.patient.patient_number} - "
            f"{self.investigation_name}"
        )
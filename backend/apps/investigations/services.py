from django.db import transaction
from django.utils import timezone


from rest_framework.exceptions import ValidationError


from .models import Investigation


@transaction.atomic
def generate_investigation_number():
    last_investigation = (
        Investigation.objects
        .select_for_update()
        .order_by("-id")
        .first()
    )

    if last_investigation is None:
        next_number = 1
    else:
        next_number = last_investigation.id + 1

    return f"INV-{next_number:06d}"

@transaction.atomic
def queue_investigation(investigation):
    if investigation.status != Investigation.STATUS_ORDERED:
        raise ValidationError(
            "Only ordered investigations can be queued."
        )

    investigation.status = Investigation.STATUS_QUEUED
    investigation.queued_at = timezone.now()

    investigation.save(
        update_fields=[
            "status",
            "queued_at",
            "updated_at",
        ]
    )

    return investigation


@transaction.atomic
def assign_investigation(investigation, user):
    if investigation.status not in [
        Investigation.STATUS_QUEUED,
        Investigation.STATUS_ORDERED,
    ]:
        raise ValidationError(
            "Only queued or ordered investigations can be assigned."
        )

    investigation.assigned_to = user

    if investigation.status == Investigation.STATUS_ORDERED:
        investigation.status = Investigation.STATUS_QUEUED
        investigation.queued_at = timezone.now()

    investigation.save(
        update_fields=[
            "assigned_to",
            "status",
            "queued_at",
            "updated_at",
        ]
    )

    return investigation


@transaction.atomic
def start_investigation(investigation, user):
    if investigation.status != Investigation.STATUS_QUEUED:
        raise ValidationError(
            "Only queued investigations can be started."
        )

    if (
        investigation.assigned_to_id is not None
        and investigation.assigned_to_id != user.id
    ):
        raise ValidationError(
            "This investigation is assigned to another user."
        )

    investigation.assigned_to = user
    investigation.status = Investigation.STATUS_IN_PROGRESS
    investigation.started_at = timezone.now()

    investigation.save(
        update_fields=[
            "assigned_to",
            "status",
            "started_at",
            "updated_at",
        ]
    )

    return investigation


@transaction.atomic
def complete_investigation(investigation, user):
    if investigation.status != Investigation.STATUS_IN_PROGRESS:
        raise ValidationError(
            "Only investigations in progress can be completed."
        )

    if (
        investigation.assigned_to_id is not None
        and investigation.assigned_to_id != user.id
    ):
        raise ValidationError(
            "This investigation is assigned to another user."
        )

    investigation.status = Investigation.STATUS_COMPLETED
    investigation.completed_at = timezone.now()

    investigation.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    return investigation


@transaction.atomic
def mark_reported(investigation):
    if investigation.status != Investigation.STATUS_COMPLETED:
        raise ValidationError(
            "Only completed investigations can be marked as reported."
        )

    investigation.status = Investigation.STATUS_REPORTED
    investigation.reported_at = timezone.now()

    investigation.save(
        update_fields=[
            "status",
            "reported_at",
            "updated_at",
        ]
    )

    return investigation


@transaction.atomic
def cancel_investigation(
    investigation,
    reason="",
):
    if investigation.status in [
        Investigation.STATUS_COMPLETED,
        Investigation.STATUS_REPORTED,
        Investigation.STATUS_CANCELLED,
    ]:
        raise ValidationError(
            "This investigation cannot be cancelled."
        )

    investigation.status = Investigation.STATUS_CANCELLED
    investigation.cancelled_at = timezone.now()
    investigation.cancellation_reason = reason

    investigation.save(
        update_fields=[
            "status",
            "cancelled_at",
            "cancellation_reason",
            "updated_at",
        ]
    )

    return investigation



@transaction.atomic
def synchronize_investigation_status(investigation):
    """
    Synchronize the generic Investigation status with the
    department-specific workflow.

    Laboratory:
        LaboratoryOrder VERIFIED -> Investigation REPORTED
        LaboratoryOrder COMPLETED -> Investigation COMPLETED

    Cancelled department workflows propagate cancellation
    to the parent Investigation.
    """

    # Laboratory workflow
    if investigation.department == Investigation.DEPARTMENT_LABORATORY:

        if not hasattr(investigation, "laboratory_order"):
            return investigation

        laboratory_order = investigation.laboratory_order

        from apps.laboratory.models import LaboratoryOrder

        if laboratory_order.status == LaboratoryOrder.STATUS_CANCELLED:
            investigation.status = Investigation.STATUS_CANCELLED
            investigation.cancelled_at = timezone.now()

            investigation.save(
                update_fields=[
                    "status",
                    "cancelled_at",
                    "updated_at",
                ]
            )

        elif laboratory_order.status == LaboratoryOrder.STATUS_VERIFIED:
            investigation.status = Investigation.STATUS_REPORTED
            investigation.reported_at = timezone.now()

            investigation.save(
                update_fields=[
                    "status",
                    "reported_at",
                    "updated_at",
                ]
            )

        elif laboratory_order.status == LaboratoryOrder.STATUS_COMPLETED:
            investigation.status = Investigation.STATUS_COMPLETED
            investigation.completed_at = timezone.now()

            investigation.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "updated_at",
                ]
            )

    return investigation
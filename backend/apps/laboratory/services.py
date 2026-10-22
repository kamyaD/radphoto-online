from django.db import transaction
from django.utils import timezone

from apps.investigations.services import synchronize_investigation_status
from rest_framework.exceptions import ValidationError

from apps.investigations.models import Investigation

from .models import (
    LaboratoryItemResult,
    LaboratoryOrder,
    LaboratoryOrderItem,
    LaboratoryPanel,
    LaboratoryPanelTest,
    LaboratoryResult,
    LaboratorySpecimen,
    LaboratoryTest,
)





@transaction.atomic
def create_laboratory_order(
    investigation,
    test,
):
    if investigation.department != (
        Investigation.DEPARTMENT_LABORATORY
    ):
        raise ValidationError(
            "Investigation does not belong to the laboratory department."
        )

    if investigation.investigation_type != (
        Investigation.TYPE_LABORATORY
    ):
        raise ValidationError(
            "Investigation type must be LABORATORY."
        )

    if hasattr(
        investigation,
        "laboratory_order",
    ):
        raise ValidationError(
            "A laboratory order already exists for this investigation."
        )

    return LaboratoryOrder.objects.create(
        investigation=investigation,
        test=test,
    )


@transaction.atomic
def collect_specimen(
    laboratory_order,
    user,
):
    if laboratory_order.status != (
        LaboratoryOrder.STATUS_PENDING
    ):
        raise ValidationError(
            "Specimen can only be collected for pending orders."
        )

    now = timezone.now()

    laboratory_order.status = (
        LaboratoryOrder.STATUS_SPECIMEN_COLLECTED
    )

    laboratory_order.collected_by = user
    laboratory_order.specimen_collected_at = now

    laboratory_order.save(
        update_fields=[
            "status",
            "collected_by",
            "specimen_collected_at",
            "updated_at",
        ]
    )

    return laboratory_order


@transaction.atomic
def start_processing(
    laboratory_order,
    user,
):
    if laboratory_order.status != (
        LaboratoryOrder.STATUS_SPECIMEN_COLLECTED
    ):
        raise ValidationError(
            "Only collected specimens can be processed."
        )

    now = timezone.now()

    laboratory_order.status = (
        LaboratoryOrder.STATUS_IN_PROGRESS
    )

    laboratory_order.processed_by = user
    laboratory_order.started_at = now

    laboratory_order.save(
        update_fields=[
            "status",
            "processed_by",
            "started_at",
            "updated_at",
        ]
    )

    return laboratory_order


@transaction.atomic
def enter_result(
    laboratory_order,
    user,
    result_value,
    unit="",
    reference_range="",
    flag=LaboratoryResult.FLAG_NORMAL,
    interpretation="",
):
    if laboratory_order.status != (
        LaboratoryOrder.STATUS_IN_PROGRESS
    ):
        raise ValidationError(
            "Results can only be entered for investigations in progress."
        )

    if hasattr(
        laboratory_order,
        "result",
    ):
        raise ValidationError(
            "A result already exists for this laboratory order."
        )

    result = LaboratoryResult.objects.create(
        laboratory_order=laboratory_order,
        result_value=result_value,
        unit=unit,
        reference_range=reference_range,
        flag=flag,
        interpretation=interpretation,
        entered_by=user,
    )

    laboratory_order.status = (
        LaboratoryOrder.STATUS_COMPLETED
    )

    laboratory_order.completed_at = timezone.now()

    laboratory_order.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    return result


@transaction.atomic
def verify_result(
    laboratory_order,
    user,
):
    if laboratory_order.status != (
        LaboratoryOrder.STATUS_COMPLETED
    ):
        raise ValidationError(
            "Only completed laboratory results can be verified."
        )

    if not hasattr(
        laboratory_order,
        "result",
    ):
        raise ValidationError(
            "Laboratory result does not exist."
        )

    laboratory_order.status = (
        LaboratoryOrder.STATUS_VERIFIED
    )

    laboratory_order.verified_by = user
    laboratory_order.verified_at = timezone.now()

    laboratory_order.save(
        update_fields=[
            "status",
            "verified_by",
            "verified_at",
            "updated_at",
        ]
    )

    return laboratory_order

@transaction.atomic
def generate_specimen_accession_number():
    last_specimen = (
        LaboratorySpecimen.objects
        .select_for_update()
        .order_by("-id")
        .first()
    )

    if last_specimen is None:
        next_number = 1
    else:
        next_number = last_specimen.id + 1

    return f"SPC-{next_number:06d}"

@transaction.atomic
def create_specimen(
    laboratory_order,
    specimen_type,
    user,
):
    if laboratory_order.status == LaboratoryOrder.STATUS_CANCELLED:
        raise ValidationError(
            "Cannot create a specimen for a cancelled laboratory order."
        )

    accession_number = generate_specimen_accession_number()

    specimen = LaboratorySpecimen.objects.create(
        laboratory_order=laboratory_order,
        accession_number=accession_number,
        specimen_type=specimen_type,
        status=LaboratorySpecimen.STATUS_COLLECTED,
        collected_by=user,
        collected_at=timezone.now(),
    )

    return specimen


@transaction.atomic
def receive_specimen(specimen, user):
    if specimen.status != LaboratorySpecimen.STATUS_COLLECTED:
        raise ValidationError(
            "Only collected specimens can be received."
        )

    specimen.status = LaboratorySpecimen.STATUS_RECEIVED
    specimen.received_by = user
    specimen.received_at = timezone.now()

    specimen.save(
        update_fields=[
            "status",
            "received_by",
            "received_at",
            "updated_at",
        ]
    )

    return specimen

@transaction.atomic
def reject_specimen(specimen, reason):
    if specimen.status == LaboratorySpecimen.STATUS_PROCESSED:
        raise ValidationError(
            "A processed specimen cannot be rejected."
        )

    if not reason or not reason.strip():
        raise ValidationError(
            "A rejection reason is required."
        )

    specimen.status = LaboratorySpecimen.STATUS_REJECTED
    specimen.rejection_reason = reason.strip()

    specimen.save(
        update_fields=[
            "status",
            "rejection_reason",
            "updated_at",
        ]
    )

    return specimen

@transaction.atomic
def add_test_to_order(laboratory_order, test):
    if laboratory_order.status == LaboratoryOrder.STATUS_CANCELLED:
        raise ValidationError(
            "Cannot add tests to a cancelled laboratory order."
        )

    item, created = LaboratoryOrderItem.objects.get_or_create(
        laboratory_order=laboratory_order,
        test=test,
    )

    if not created:
        raise ValidationError(
            "This test already exists on the laboratory order."
        )

    return item

@transaction.atomic
def add_panel_to_order(laboratory_order, panel):
    if laboratory_order.status == LaboratoryOrder.STATUS_CANCELLED:
        raise ValidationError(
            "Cannot add a panel to a cancelled laboratory order."
        )

    items = []

    for panel_test in panel.panel_tests.select_related("test").all():
        item, created = LaboratoryOrderItem.objects.get_or_create(
            laboratory_order=laboratory_order,
            test=panel_test.test,
        )

        if created:
            items.append(item)

    if not items:
        raise ValidationError(
            "No new tests were added from this panel."
        )

    return items

@transaction.atomic
def start_item_processing(order_item, user):
    if order_item.status != LaboratoryOrderItem.STATUS_PENDING:
        raise ValidationError(
            "Only pending laboratory tests can be started."
        )

    if order_item.specimen_id is None:
        raise ValidationError(
            "A specimen must be assigned before processing the test."
        )

    if order_item.specimen.status not in [
        LaboratorySpecimen.STATUS_RECEIVED,
        LaboratorySpecimen.STATUS_PROCESSING,
    ]:
        raise ValidationError(
            "The specimen must be received before processing the test."
        )

    now = timezone.now()

    if order_item.specimen.status == LaboratorySpecimen.STATUS_RECEIVED:
        order_item.specimen.status = LaboratorySpecimen.STATUS_PROCESSING
        order_item.specimen.save(
            update_fields=["status", "updated_at"]
        )

    order_item.status = LaboratoryOrderItem.STATUS_IN_PROGRESS
    order_item.started_at = now

    order_item.save(
        update_fields=[
            "status",
            "started_at",
            "updated_at",
        ]
    )

    return order_item

@transaction.atomic
def enter_item_result(
    order_item,
    user,
    result_value,
    unit="",
    reference_range="",
    flag=LaboratoryItemResult.FLAG_NORMAL,
    interpretation="",
):
    if order_item.status != LaboratoryOrderItem.STATUS_IN_PROGRESS:
        raise ValidationError(
            "The laboratory test must be in progress before entering a result."
        )

    if hasattr(order_item, "result"):
        raise ValidationError(
            "A result already exists for this test."
        )

    result = LaboratoryItemResult.objects.create(
        order_item=order_item,
        result_value=result_value,
        unit=unit,
        reference_range=reference_range,
        flag=flag,
        interpretation=interpretation,
        entered_by=user,
    )

    order_item.status = LaboratoryOrderItem.STATUS_COMPLETED
    order_item.completed_at = timezone.now()

    order_item.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    return result


@transaction.atomic
def verify_item_result(order_item, user):
    if order_item.status != LaboratoryOrderItem.STATUS_COMPLETED:
        raise ValidationError(
            "Only completed laboratory tests can be verified."
        )

    if not hasattr(order_item, "result"):
        raise ValidationError(
            "This test does not have a result."
        )

    order_item.status = LaboratoryOrderItem.STATUS_VERIFIED
    order_item.verified_by = user
    order_item.verified_at = timezone.now()

    order_item.save(
        update_fields=[
            "status",
            "verified_by",
            "verified_at",
            "updated_at",
        ]
    )

    synchronize_laboratory_order_status(
        order_item.laboratory_order
    )
    synchronize_specimen_status(order_item.specimen)
    synchronize_investigation_status(
        order_item.laboratory_order.investigation
    )

    return order_item



@transaction.atomic
def synchronize_laboratory_order_status(laboratory_order):
    items = laboratory_order.items.all()

    if not items.exists():
        return laboratory_order

    if items.filter(
        status=LaboratoryOrderItem.STATUS_CANCELLED
    ).exists():
        return laboratory_order

    if items.filter(
        status=LaboratoryOrderItem.STATUS_VERIFIED
    ).count() == items.count():
        laboratory_order.status = LaboratoryOrder.STATUS_VERIFIED
        laboratory_order.verified_at = timezone.now()

        laboratory_order.save(
            update_fields=[
                "status",
                "verified_at",
                "updated_at",
            ]
        )

    elif items.filter(
        status=LaboratoryOrderItem.STATUS_COMPLETED
    ).exists():
        laboratory_order.status = LaboratoryOrder.STATUS_COMPLETED

        laboratory_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    return laboratory_order




@transaction.atomic
def synchronize_specimen_status(specimen):
    items = specimen.order_items.all()

    if not items.exists():
        return specimen

    if items.filter(
        status=LaboratoryOrderItem.STATUS_CANCELLED
    ).exists():
        return specimen

    if items.filter(
        status__in=[
            LaboratoryOrderItem.STATUS_PENDING,
            LaboratoryOrderItem.STATUS_IN_PROGRESS,
            LaboratoryOrderItem.STATUS_COMPLETED,
        ]
    ).exists():
        return specimen

    if items.filter(
        status=LaboratoryOrderItem.STATUS_VERIFIED
    ).count() == items.count():
        specimen.status = LaboratorySpecimen.STATUS_PROCESSED

        specimen.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    return specimen


from django.db import transaction

from .models import Facility


@transaction.atomic
def generate_facility_number():
    """
    Generate the next RadPhoto facility number.

    Example:
        FAC-000001
        FAC-000002
    """

    last_facility = (
        Facility.objects
        .select_for_update()
        .order_by("-id")
        .first()
    )

    if last_facility is None:
        next_number = 1
    else:
        next_number = last_facility.id + 1

    return f"FAC-{next_number:06d}"
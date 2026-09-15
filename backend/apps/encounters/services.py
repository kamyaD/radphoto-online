from django.db import transaction

from .models import Encounter


@transaction.atomic
def generate_encounter_number():
    last_encounter = (
        Encounter.objects
        .select_for_update()
        .order_by("-id")
        .first()
    )

    if last_encounter is None:
        next_number = 1
    else:
        next_number = last_encounter.id + 1

    return f"ENC-{next_number:06d}"
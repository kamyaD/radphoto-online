from django.db import transaction

from .models import Patient


@transaction.atomic
def generate_patient_number():
    last_patient = (
        Patient.objects
        .select_for_update()
        .order_by("-id")
        .first()
    )

    if last_patient is None:
        next_number = 1
    else:
        next_number = last_patient.id + 1

    return f"PAT-{next_number:06d}"
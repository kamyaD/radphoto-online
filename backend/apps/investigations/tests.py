from django.test import TestCase

from apps.investigations.models import Investigation
from apps.investigations.services import (
    synchronize_investigation_status,
)


class InvestigationLifecycleTest(TestCase):

    def test_laboratory_investigation_requires_laboratory_order(self):
        investigation = Investigation.objects.create(
            facility_id=1,
            patient_id=1,
            encounter_id=1,
            ordered_by_id=1,
            department=Investigation.DEPARTMENT_LABORATORY,
            investigation_type=Investigation.TYPE_LABORATORY,
            investigation_name="CBC",
        )

        result = synchronize_investigation_status(
            investigation
        )

        self.assertEqual(
            result.status,
            Investigation.STATUS_ORDERED,
        )
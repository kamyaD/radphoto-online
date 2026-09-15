from rest_framework import serializers

from .models import Investigation


class InvestigationSerializer(serializers.ModelSerializer):
    patient_number = serializers.CharField(
        source="patient.patient_number",
        read_only=True,
    )

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True,
    )

    encounter_number = serializers.CharField(
        source="encounter.encounter_number",
        read_only=True,
    )

    ordered_by_username = serializers.CharField(
        source="ordered_by.username",
        read_only=True,
    )

    investigation_number = serializers.CharField(
        read_only=True,
    )
    assigned_to_username = serializers.CharField(
        source="assigned_to.username",
        read_only=True,
    )

    class Meta:
        model = Investigation

        fields = [
            "id",
            "investigation_number",

            "facility",

            "patient",
            "patient_number",
            "patient_name",

            "encounter",
            "encounter_number",

            "ordered_by",
            "ordered_by_username",

            "department",
            "investigation_type",
            "investigation_name",

            "priority",
            "clinical_indication",

            "status",

            "ordered_at",
            "updated_at",
            "completed_at",

            "cancelled_at",
            "cancellation_reason",
            "assigned_to",
            "assigned_to_username",
            "queued_at",
            "started_at",
            "reported_at",
        ]

        read_only_fields = [
            "id",
            "investigation_number",
            "patient_number",
            "patient_name",
            "encounter_number",
            "ordered_by",
            "ordered_by_username",
            "ordered_at",
            "updated_at",
            "completed_at",
            "cancelled_at",
            "assigned_to_username",
            "queued_at",
            "started_at",
            "updated_at",
            "completed_at",
            "reported_at",
            "cancelled_at",
        ]

    def validate(self, attrs):
        facility = attrs.get("facility")
        patient = attrs.get("patient")
        encounter = attrs.get("encounter")

        if facility and patient:
            if patient.facility_id != facility.id:
                raise serializers.ValidationError({
                    "patient": (
                        "The selected patient does not belong "
                        "to the selected facility."
                    )
                })

            if not patient.is_active:
                raise serializers.ValidationError({
                    "patient": "The selected patient is inactive."
                })

        if facility and encounter:
            if encounter.facility_id != facility.id:
                raise serializers.ValidationError({
                    "encounter": (
                        "The selected encounter does not belong "
                        "to the selected facility."
                    )
                })

        if patient and encounter:
            if encounter.patient_id != patient.id:
                raise serializers.ValidationError({
                    "encounter": (
                        "The selected encounter does not belong "
                        "to the selected patient."
                    )
                })

        return attrs

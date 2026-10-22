from django.utils import timezone
from rest_framework import serializers

from .models import Encounter


class EncounterSerializer(serializers.ModelSerializer):
    patient_number = serializers.CharField(
        source="patient.patient_number",
        read_only=True,
    )

    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True,
    )

    encounter_number = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Encounter

        fields = [
            "id",
            "encounter_number",
            "facility",
            "patient",
            "patient_number",
            "patient_name",
            "encounter_type",
            "status",
            "attending_user",
            "chief_complaint",
            "clinical_notes",
            "registration_time",
            "updated_at",
            "completed_at",
        ]

        read_only_fields = [
            "id",
            "encounter_number",
            "patient_number",
            "patient_name",
            "registration_time",
            "updated_at",
            "completed_at",
        ]

    def validate(self, attrs):
        facility = attrs.get("facility")
        patient = attrs.get("patient")

        if facility and patient:
            if patient.facility_id != facility.id:
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "The selected patient does not "
                            "belong to the selected facility."
                        )
                    }
                )

            if not patient.is_active:
                raise serializers.ValidationError(
                    {
                        "patient": (
                            "The selected patient is inactive."
                        )
                    }
                )

        return attrs

    def validate_completed_at(self, value):
        if value and value > timezone.now():
            raise serializers.ValidationError(
                "Completion time cannot be in the future."
            )

        return value
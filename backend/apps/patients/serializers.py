from django.utils import timezone
from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Patient
        fields = [
            "id",
            "patient_number",
            "facility",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "date_of_birth",
            "sex",
            "phone_number",
            "email",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "registration_date",
            "updated_at",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "patient_number",
            "full_name",
            "registration_date",
            "updated_at",
        ]

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name cannot be empty."
            )

        return value

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name cannot be empty."
            )

        return value

    def validate_date_of_birth(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )

        return value
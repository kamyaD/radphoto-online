from rest_framework import serializers

from .models import Facility


class FacilitySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Facility

        fields = [
            "id",
            "facility_number",
            "name",
            "registration_number",
            "phone_number",
            "email",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "facility_number",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Facility name cannot be empty."
            )

        return value
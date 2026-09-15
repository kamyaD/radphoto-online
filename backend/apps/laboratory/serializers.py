from rest_framework import serializers

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


class LaboratoryTestSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = LaboratoryTest

        fields = [
            "id",
            "code",
            "name",
            "category",
            "specimen_type",
            "description",
            "unit",
            "reference_range",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_code(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Test code cannot be empty."
            )

        return value

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Test name cannot be empty."
            )

        return value


class LaboratoryResultSerializer(
    serializers.ModelSerializer
):
    entered_by_username = serializers.CharField(
        source="entered_by.username",
        read_only=True,
    )

    class Meta:
        model = LaboratoryResult

        fields = [
            "id",
            "laboratory_order",
            "result_value",
            "unit",
            "reference_range",
            "flag",
            "interpretation",
            "entered_by",
            "entered_by_username",
            "entered_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "entered_by",
            "entered_by_username",
            "entered_at",
            "updated_at",
        ]


class LaboratoryOrderSerializer(
    serializers.ModelSerializer
):
    investigation_number = serializers.CharField(
        source="investigation.investigation_number",
        read_only=True,
    )

    patient_number = serializers.CharField(
        source="investigation.patient.patient_number",
        read_only=True,
    )

    patient_name = serializers.CharField(
        source="investigation.patient.full_name",
        read_only=True,
    )

    test_name = serializers.CharField(
        source="test.name",
        read_only=True,
    )

    test_code = serializers.CharField(
        source="test.code",
        read_only=True,
    )

    class Meta:
        model = LaboratoryOrder

        fields = [
            "id",
            "investigation",
            "investigation_number",
            "patient_number",
            "patient_name",
            "test",
            "test_code",
            "test_name",
            "status",
            "collected_by",
            "processed_by",
            "verified_by",
            "specimen_collected_at",
            "started_at",
            "completed_at",
            "verified_at",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "investigation_number",
            "patient_number",
            "patient_name",
            "test_code",
            "test_name",
            "collected_by",
            "processed_by",
            "verified_by",
            "specimen_collected_at",
            "started_at",
            "completed_at",
            "verified_at",
            "created_at",
            "updated_at",
        ]

class LaboratoryPanelTestSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(
        source="test.name",
        read_only=True,
    )

    test_code = serializers.CharField(
        source="test.code",
        read_only=True,
    )

    class Meta:
        model = LaboratoryPanelTest
        fields = [
            "id",
            "panel",
            "test",
            "test_code",
            "test_name",
            "display_order",
            "is_required",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "test_code",
            "test_name",
            "created_at",
        ]

class LaboratoryPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaboratoryPanel
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_code(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Panel code cannot be empty."
            )

        return value

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Panel name cannot be empty."
            )

        return value

class LaboratorySpecimenSerializer(serializers.ModelSerializer):
    collected_by_username = serializers.CharField(
        source="collected_by.username",
        read_only=True,
    )

    received_by_username = serializers.CharField(
        source="received_by.username",
        read_only=True,
    )

    class Meta:
        model = LaboratorySpecimen

        fields = [
            "id",
            "laboratory_order",
            "accession_number",
            "specimen_type",
            "status",
            "collected_by",
            "collected_by_username",
            "received_by",
            "received_by_username",
            "collected_at",
            "received_at",
            "rejection_reason",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "accession_number",
            "collected_by",
            "collected_by_username",
            "received_by",
            "received_by_username",
            "collected_at",
            "received_at",
            "created_at",
            "updated_at",
        ]


class LaboratoryOrderItemSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(
        source="test.name",
        read_only=True,
    )

    test_code = serializers.CharField(
        source="test.code",
        read_only=True,
    )

    specimen_accession_number = serializers.CharField(
        source="specimen.accession_number",
        read_only=True,
    )

    class Meta:
        model = LaboratoryOrderItem

        fields = [
            "id",
            "laboratory_order",
            "test",
            "test_code",
            "test_name",
            "specimen",
            "specimen_accession_number",
            "status",
            "started_at",
            "completed_at",
            "verified_at",
            "verified_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "test_code",
            "test_name",
            "specimen_accession_number",
            "status",
            "started_at",
            "completed_at",
            "verified_at",
            "verified_by",
            "created_at",
            "updated_at",
        ]

class LaboratoryItemResultSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(
        source="order_item.test.name",
        read_only=True,
    )

    test_code = serializers.CharField(
        source="order_item.test.code",
        read_only=True,
    )

    entered_by_username = serializers.CharField(
        source="entered_by.username",
        read_only=True,
    )

    class Meta:
        model = LaboratoryItemResult

        fields = [
            "id",
            "order_item",
            "test_name",
            "test_code",
            "result_value",
            "unit",
            "reference_range",
            "flag",
            "interpretation",
            "entered_by",
            "entered_by_username",
            "entered_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "test_name",
            "test_code",
            "entered_by",
            "entered_by_username",
            "entered_at",
            "updated_at",
        ]
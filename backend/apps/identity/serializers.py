from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import FacilityMembership, User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        attrs["user"] = user

        return attrs


class FacilityMembershipSerializer(
    serializers.ModelSerializer
):
    facility_name = serializers.CharField(
        source="facility.name",
        read_only=True,
    )

    facility_number = serializers.CharField(
        source="facility.facility_number",
        read_only=True,
    )

    class Meta:
        model = FacilityMembership
        fields = [
            "id",
            "facility",
            "facility_name",
            "facility_number",
            "role",
            "is_active",
        ]


class UserSerializer(serializers.ModelSerializer):
    memberships = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "is_staff",
            "memberships",
        ]

    def get_memberships(self, obj):
        memberships = (
            obj.facility_memberships
            .filter(is_active=True)
            .select_related("facility")
        )

        return FacilityMembershipSerializer(
            memberships,
            many=True,
        ).data
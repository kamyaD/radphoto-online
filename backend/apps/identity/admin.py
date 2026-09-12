from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from .models import FacilityMembership


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "RadPhoto Information",
            {
                "fields": (
                    "phone_number",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(FacilityMembership)
class FacilityMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "facility",
        "role",
        "is_active",
    )

    list_filter = (
        "role",
        "is_active",
        "facility",
    )

    search_fields = (
        "user__username",
        "user__email",
        "facility__name",
        "facility__facility_number",
    )
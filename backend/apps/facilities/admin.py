from django.contrib import admin

from .models import Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = (
        "facility_number",
        "name",
        "phone_number",
        "email",
        "is_active",
    )

    search_fields = (
        "facility_number",
        "name",
        "registration_number",
    )

    list_filter = (
        "is_active",
    )



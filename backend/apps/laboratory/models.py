from django.db import models

from django.conf import settings

from apps.investigations.models import Investigation


class LaboratoryTest(models.Model):
    CATEGORY_HAEMATOLOGY = "HAEMATOLOGY"
    CATEGORY_CHEMISTRY = "CHEMISTRY"
    CATEGORY_MICROBIOLOGY = "MICROBIOLOGY"
    CATEGORY_IMMUNOLOGY = "IMMUNOLOGY"
    CATEGORY_SEROLOGY = "SEROLOGY"
    CATEGORY_URINALYSIS = "URINALYSIS"
    CATEGORY_OTHER = "OTHER"

    CATEGORY_CHOICES = [
        (CATEGORY_HAEMATOLOGY, "Haematology"),
        (CATEGORY_CHEMISTRY, "Clinical Chemistry"),
        (CATEGORY_MICROBIOLOGY, "Microbiology"),
        (CATEGORY_IMMUNOLOGY, "Immunology"),
        (CATEGORY_SEROLOGY, "Serology"),
        (CATEGORY_URINALYSIS, "Urinalysis"),
        (CATEGORY_OTHER, "Other"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
    )

    specimen_type = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    unit = models.CharField(
        max_length=50,
        blank=True,
    )

    reference_range = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["category", "is_active"]
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class LaboratoryOrder(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_SPECIMEN_COLLECTED = "SPECIMEN_COLLECTED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_VERIFIED = "VERIFIED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SPECIMEN_COLLECTED, "Specimen Collected"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_VERIFIED, "Verified"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    investigation = models.OneToOneField(
        Investigation,
        on_delete=models.PROTECT,
        related_name="laboratory_order",
    )

    test = models.ForeignKey(
        LaboratoryTest,
        on_delete=models.PROTECT,
        related_name="laboratory_orders",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="collected_specimens",
        null=True,
        blank=True,
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="processed_laboratory_orders",
        null=True,
        blank=True,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="verified_laboratory_orders",
        null=True,
        blank=True,
    )

    specimen_collected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "created_at"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.investigation.investigation_number} - "
            f"{self.test.name}"
        )


class LaboratoryResult(models.Model):
    FLAG_NORMAL = "NORMAL"
    FLAG_LOW = "LOW"
    FLAG_HIGH = "HIGH"
    FLAG_CRITICAL = "CRITICAL"
    FLAG_ABNORMAL = "ABNORMAL"

    FLAG_CHOICES = [
        (FLAG_NORMAL, "Normal"),
        (FLAG_LOW, "Low"),
        (FLAG_HIGH, "High"),
        (FLAG_CRITICAL, "Critical"),
        (FLAG_ABNORMAL, "Abnormal"),
    ]

    laboratory_order = models.OneToOneField(
        LaboratoryOrder,
        on_delete=models.PROTECT,
        related_name="result",
    )

    result_value = models.TextField()

    unit = models.CharField(
        max_length=50,
        blank=True,
    )

    reference_range = models.CharField(
        max_length=255,
        blank=True,
    )

    flag = models.CharField(
        max_length=20,
        choices=FLAG_CHOICES,
        default=FLAG_NORMAL,
    )

    interpretation = models.TextField(
        blank=True,
    )

    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="entered_laboratory_results",
    )

    entered_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-entered_at"]

    def __str__(self):
        return (
            f"{self.laboratory_order} - "
            f"{self.flag}"
        )

class LaboratoryPanel(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    tests = models.ManyToManyField(
        LaboratoryTest,
        through="LaboratoryPanelTest",
        related_name="panels",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class LaboratoryPanelTest(models.Model):
    panel = models.ForeignKey(
        LaboratoryPanel,
        on_delete=models.CASCADE,
        related_name="panel_tests",
    )

    test = models.ForeignKey(
        LaboratoryTest,
        on_delete=models.PROTECT,
        related_name="panel_test_memberships",
    )

    display_order = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["panel", "test"],
                name="unique_test_per_panel",
            ),
        ]

    def __str__(self):
        return f"{self.panel.code} - {self.test.code}"


class LaboratorySpecimen(models.Model):
    STATUS_COLLECTED = "COLLECTED"
    STATUS_RECEIVED = "RECEIVED"
    STATUS_PROCESSING = "PROCESSING"
    STATUS_PROCESSED = "PROCESSED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_COLLECTED, "Collected"),
        (STATUS_RECEIVED, "Received"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_REJECTED, "Rejected"),
    ]

    laboratory_order = models.ForeignKey(
        LaboratoryOrder,
        on_delete=models.PROTECT,
        related_name="specimens",
    )

    accession_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
    )

    specimen_type = models.CharField(max_length=100)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_COLLECTED,
    )

    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="collected_laboratory_specimens",
        null=True,
        blank=True,
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="received_laboratory_specimens",
        null=True,
        blank=True,
    )

    collected_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["laboratory_order", "status"]
            ),
            models.Index(
                fields=["accession_number"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.accession_number} - "
            f"{self.specimen_type}"
        )

class LaboratoryOrderItem(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_VERIFIED = "VERIFIED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_VERIFIED, "Verified"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    laboratory_order = models.ForeignKey(
        LaboratoryOrder,
        on_delete=models.PROTECT,
        related_name="items",
    )

    test = models.ForeignKey(
        LaboratoryTest,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    specimen = models.ForeignKey(
        LaboratorySpecimen,
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="verified_laboratory_items",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["laboratory_order", "test"],
                name="unique_test_per_laboratory_order",
            ),
        ]
        indexes = [
            models.Index(
                fields=["laboratory_order", "status"]
            ),
            models.Index(
                fields=["test", "status"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.laboratory_order} - "
            f"{self.test.code}"
        )

class LaboratoryItemResult(models.Model):
    FLAG_NORMAL = "NORMAL"
    FLAG_LOW = "LOW"
    FLAG_HIGH = "HIGH"
    FLAG_CRITICAL = "CRITICAL"
    FLAG_ABNORMAL = "ABNORMAL"

    FLAG_CHOICES = [
        (FLAG_NORMAL, "Normal"),
        (FLAG_LOW, "Low"),
        (FLAG_HIGH, "High"),
        (FLAG_CRITICAL, "Critical"),
        (FLAG_ABNORMAL, "Abnormal"),
    ]

    order_item = models.OneToOneField(
        LaboratoryOrderItem,
        on_delete=models.PROTECT,
        related_name="result",
    )

    result_value = models.TextField()

    unit = models.CharField(
        max_length=50,
        blank=True,
    )

    reference_range = models.CharField(
        max_length=255,
        blank=True,
    )

    flag = models.CharField(
        max_length=20,
        choices=FLAG_CHOICES,
        default=FLAG_NORMAL,
    )

    interpretation = models.TextField(
        blank=True
    )

    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="entered_laboratory_item_results",
    )

    entered_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-entered_at"]

    def __str__(self):
        return (
            f"{self.order_item.test.code} - "
            f"{self.flag}"
        )
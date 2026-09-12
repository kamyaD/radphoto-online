class UserRole:
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    FACILITY_ADMIN = "FACILITY_ADMIN"
    DOCTOR = "DOCTOR"
    RADIOLOGIST = "RADIOLOGIST"
    RADIOGRAPHER = "RADIOGRAPHER"
    LAB_TECHNICIAN = "LAB_TECHNICIAN"
    PATHOLOGIST = "PATHOLOGIST"
    CARDIOLOGIST = "CARDIOLOGIST"
    RECEPTIONIST = "RECEPTIONIST"
    BILLING_OFFICER = "BILLING_OFFICER"
    MANAGEMENT = "MANAGEMENT"

    CHOICES = [
        (SYSTEM_ADMIN, "System Administrator"),
        (FACILITY_ADMIN, "Facility Administrator"),
        (DOCTOR, "Doctor"),
        (RADIOLOGIST, "Radiologist"),
        (RADIOGRAPHER, "Radiographer"),
        (LAB_TECHNICIAN, "Laboratory Technician"),
        (PATHOLOGIST, "Pathologist"),
        (CARDIOLOGIST, "Cardiologist"),
        (RECEPTIONIST, "Receptionist"),
        (BILLING_OFFICER, "Billing Officer"),
        (MANAGEMENT, "Management"),
    ]
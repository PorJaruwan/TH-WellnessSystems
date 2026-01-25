# app/db/models/__init__.py

from app.db.base import Base

# ----- Core Settings ----- #
from .core_settings import (
    Company, Department, Location, Building,
    Room, RoomService, RoomAvailability,
    Service, ServiceType,
    Country, Province, City, District,
    Currency, Language, Geography,
)

# ----- Staff Settings ----- #
from .staff_settings import (
    Staff, StaffDepartment, StaffLocation, StaffService,
    StaffTemplate, StaffWorkPattern, StaffLeave,
)

# ----- Patient Settings (patient, patient_addr, alerts, allergies, etc.) ----- #
from .patient_settings import (
    Patient, PatientAddress, PatientImage, PatientPhoto,
    Alert, Allergy, MarketingStaff, PatientType, Profession, SaleStaff, Source,
)

__all__ = [
    "Base",

    # Core settings
    "Company", "Department", "Location", "Building",
    "Room", "RoomService", "RoomAvailability",
    "Service", "ServiceType",
    "Country", "Province", "City", "District",
    "Currency", "Language", "Geography",

    # Staff settings
    "Staff", "StaffDepartment", "StaffLocation", "StaffService",
    "StaffTemplate", "StaffWorkPattern", "StaffLeave",

    # Patient settings
    "Patient",
    "PatientAddress", "PatientImage", "PatientPhoto",
    "Alert", "Allergy", "MarketingStaff", "PatientType", "Profession", "SaleStaff", "Source",
]

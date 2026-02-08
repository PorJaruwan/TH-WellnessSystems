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
    #StaffAvailabilities, StaffUnavailabilities,
)


# ----- Patient Settings (patient, patient_addr, alerts, allergies, etc.) ----- #
from .patient_settings import (
    Patient, PatientAddress, PatientImage, PatientPhoto,
    Alert, Allergy, MarketingStaff, PatientType, Profession, SaleStaff, Source,
)

from .booking_settings import (
    Booking, BookingViewConfig, BookingStatusHistory, BookingStaff
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
    #"StaffAvailabilities", "StaffUnavailabilities",

    # Patient settings
    "Patient",
    "PatientAddress", "PatientImage", "PatientPhoto",
    "Alert", "Allergy", "MarketingStaff", "PatientType", "Profession", "SaleStaff", "Source",
    
    # Booking settings
    "Booking", "BookingViewConfig", "BookingStatusHistory", "BookingStaff",
]

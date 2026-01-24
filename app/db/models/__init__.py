#app.db.models.__init__.py

from app.db.base import Base

# ----- Core Settings ----- #
from .core_settings import (
    Company, Department, Location, Building, 
    Room, RoomService, RoomAvailability, 
    Service, ServiceType
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
    # Patients settings (child and related)
    "Patient", 
    "PatientAddress", "PatientImage", "PatientPhoto",
    "Alert", "Allergy", "MarketingStaff", "PatientType", "Profession", "SaleStaff", "Source",
    ]
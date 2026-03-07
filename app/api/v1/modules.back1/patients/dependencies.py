# app/api/v1/modules/patients/dependencies.py
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

from app.api.v1.modules.patients.repositories.patients_crud_repository import PatientsCrudRepository
from app.api.v1.modules.patients.repositories.patients_search_repository import PatientsSearchRepository
from app.api.v1.modules.patients.repositories.patients_read_repository import PatientsReadRepository

from app.api.v1.modules.patients.services.patients_crud_service import PatientsCrudService
from app.api.v1.modules.patients.services.patients_search_service import PatientsSearchService
from app.api.v1.modules.patients.services.patients_read_service import PatientsReadService


# ✅ Standard DI factories (ใช้เหมือนกันทุก router 100%)
def get_patients_crud_service(db: AsyncSession = Depends(get_db)) -> PatientsCrudService:
    return PatientsCrudService(db=db, repo=PatientsCrudRepository(db))


def get_patients_search_service(db: AsyncSession = Depends(get_db)) -> PatientsSearchService:
    return PatientsSearchService(PatientsSearchRepository(db))


def get_patients_read_service(db: AsyncSession = Depends(get_db)) -> PatientsReadService:
    return PatientsReadService(PatientsReadRepository(db))


# =========================================================
# Sub-resources (profiles/addresses/images/photos)
# =========================================================
from app.api.v1.modules.patients.repositories.patient_addresses_repository import PatientAddressesRepository
from app.api.v1.modules.patients.services.patient_addresses_service_v2 import PatientAddressesService

from app.api.v1.modules.patients.repositories.patient_images_repository import PatientImagesRepository
from app.api.v1.modules.patients.services.patient_images_service_v2 import PatientImagesService

from app.api.v1.modules.patients.repositories.patient_photos_repository import PatientPhotosRepository
from app.api.v1.modules.patients.services.patient_photos_service_v2 import PatientPhotosService

from app.api.v1.modules.patients.repositories.patient_profiles_repository import PatientProfilesRepository
from app.api.v1.modules.patients.services.patient_profiles_service_v2 import PatientProfilesService


def get_patient_addresses_service(db: AsyncSession = Depends(get_db)) -> PatientAddressesService:
    return PatientAddressesService(PatientAddressesRepository(db))


def get_patient_images_service(db: AsyncSession = Depends(get_db)) -> PatientImagesService:
    return PatientImagesService(PatientImagesRepository(db))


def get_patient_photos_service(db: AsyncSession = Depends(get_db)) -> PatientPhotosService:
    return PatientPhotosService(PatientPhotosRepository(db))


def get_patient_profiles_service(db: AsyncSession = Depends(get_db)) -> PatientProfilesService:
    return PatientProfilesService(PatientProfilesRepository(db))

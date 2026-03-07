# Patients module refactor pack

Changes included:
- routers/__init__.py now exports routers only (no APIRouter include_router side-effects).
  ✅ Update your main api_router include to explicitly include each router from patients.routers.
- PatientsCrudService is now the transaction boundary (commit/rollback), repository is DB-only (flush/refresh).
- Added V2 CRUD envelopes aligned with ResponseHandler.success_from_request(data={"items": ...}).
- Removed ResponseCode.DATA references inside patients module (aligned with current ResponseCode in ResponseHandler.py).

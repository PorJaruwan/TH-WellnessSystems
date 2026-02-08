# app/api/v1/_templates/template_router_standard.py
# -------------------------------------------------
# Standard Router Boilerplate (patients-style)
# - ResponseHandler / ResponseCode / UnicodeJSONResponse
# - limit/offset + filters + total/count
# - NOT_FOUND / EMPTY / INVALID mapping
# - Level 3 request models (APIBaseModel extra=forbid)
# - Type-safe envelopes: SuccessEnvelope[T] | ErrorEnvelope
#
# HOW TO USE:
# 1) Copy this file into your module folder, e.g.
#    app/api/v1/locations/locations.py  or  app/api/v1/patients/patients.py
# 2) Replace placeholders marked with "TODO:"
# 3) Keep helpers unchanged to enforce standard responses across modules
# -------------------------------------------------

from __future__ import annotations

from urllib.parse import unquote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

# ==========================================================
# TODO: Replace these imports with your module's models/envelopes
# ==========================================================
# from app.api.v1.models.<module>_model import (
#     CreateModel,
#     UpdateModel,
#     UpdateNoteModel,          # optional
#     ActionBodyModel,          # optional
#     SearchEnvelope,
#     ByIdEnvelope,
#     CreateEnvelope,
#     UpdateEnvelope,
#     UpdateNoteEnvelope,       # optional
#     ActionEnvelope,           # optional
#     HistoryEnvelope,          # optional
# )

# ==========================================================
# TODO: Replace these imports with your module's services
# ==========================================================
# from app.api.v1.services.<module>_service import (
#     search_service,
#     get_by_id_service,
#     create_service,
#     update_by_id_service,
#     update_note_service,      # optional
#     action_service,           # optional
#     history_service,          # optional
# )

# ==========================================================
# TODO: Configure router prefix/tags
# ==========================================================
router = APIRouter(
    prefix="/<module>",
    tags=["<Module>"],
)


# ==========================================================
# Helpers (keep as-is)
# ==========================================================
def _data_code(key: str, default_code: str, default_message: str):
    """
    Safe getter for ResponseCode.DATA[key] to avoid KeyError.
    Returns tuple (error_code, message)
    """
    try:
        return ResponseCode.DATA[key]
    except Exception:
        return (default_code, default_message)


def _handle_http_exc_as_response(e: HTTPException, *, details: dict | None = None):
    """
    Convert HTTPException -> ResponseHandler.error (patients-style)
      - 404 -> NOT_FOUND
      - 400/422 -> INVALID
    """
    details = details or {}

    if e.status_code == 404:
        return ResponseHandler.error(
            *_data_code("NOT_FOUND", "NOT_FOUND", "Not found"),
            details=details or {"detail": str(e.detail)},
        )

    if e.status_code in (400, 422):
        return ResponseHandler.error(
            *_data_code("INVALID", "INVALID", "Invalid request"),
            details=details or {"detail": str(e.detail)},
        )

    # For other HTTPException, let FastAPI handle it (or extend mapping later)
    raise e


# ==========================================================
# Standard Search/List Endpoint (limit/offset + filters)
# ==========================================================
@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    # TODO: set response_model=SearchEnvelope
    # response_model=SearchEnvelope,
    response_model_exclude_none=True,
)
async def search_items(
    db: AsyncSession = Depends(get_db),
    # TODO: customize query params (q/company_code/etc.)
    q: str = Query(default="", description="keyword search"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {
        "q": unquote(q),
        # TODO: add more filters here
    }

    try:
        # TODO: call your search service with limit/offset
        # data = await search_service(q=filters["q"], limit=limit, offset=offset)
        #
        # total = int(getattr(data, "total", 0) or 0)
        # items = getattr(data, "items", None) or []

        # --- placeholders ---
        total = 0
        items = []

        if total == 0:
            return ResponseHandler.error(
                *_data_code("EMPTY", "EMPTY", "No data found"),
                details={"filters": filters},
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={
                "total": total,
                "count": len(items),
                "limit": limit,
                "offset": offset,
                "filters": filters,
                # TODO: rename "items" to your entity plural (e.g., "patients"/"locations")
                "items": items,
            },
        )

    except HTTPException as e:
        return _handle_http_exc_as_response(
            e, details={"filters": filters, "detail": str(e.detail)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Standard Get-by-id Endpoint (NOT_FOUND)
# ==========================================================
@router.get(
    "/{id:uuid}",
    response_class=UnicodeJSONResponse,
    # TODO: set response_model=ByIdEnvelope
    # response_model=ByIdEnvelope,
    response_model_exclude_none=True,
)
async def get_by_id(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        # TODO: b = await get_by_id_service(item_id=item_id)
        b = None  # placeholder

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            # TODO: rename key to entity name: {"location": b} / {"patient": b}
            data={"item": b},
        )

    except HTTPException as e:
        return _handle_http_exc_as_response(
            e, details={"item_id": str(item_id), "detail": str(e.detail)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Standard Create Endpoint (REGISTERED, INVALID)
# ==========================================================
@router.post(
    "",
    response_class=UnicodeJSONResponse,
    # TODO: set response_model=CreateEnvelope
    # response_model=CreateEnvelope,
    response_model_exclude_none=True,
)
async def create_item(
    payload,  # TODO: type: CreateModel
    db: AsyncSession = Depends(get_db),
):
    try:
        # TODO: created = await create_service(payload)
        created = None  # placeholder

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            # TODO: {"location": created} / {"patient": created}
            data={"item": created},
        )

    except HTTPException as e:
        return _handle_http_exc_as_response(e, details={"detail": str(e.detail)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Standard Update-by-id Endpoint (UPDATED, NOT_FOUND, INVALID)
# ==========================================================
@router.patch(
    "/{id:uuid}",
    response_class=UnicodeJSONResponse,
    # TODO: set response_model=UpdateEnvelope
    # response_model=UpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_by_id(
    item_id: UUID,
    payload,  # TODO: type: UpdateModel (Level 3, forbid extra)
    db: AsyncSession = Depends(get_db),
):
    try:
        updates = payload.model_dump(exclude_unset=True)

        if not updates:
            return ResponseHandler.error(
                *_data_code("INVALID", "INVALID", "Invalid request"),
                details={"item_id": str(item_id), "detail": "No fields to update"},
            )

        # TODO: updated = await update_by_id_service(item_id=item_id, payload=updates)
        updated = None  # placeholder

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            # TODO: {"location": updated} / {"patient": updated}
            data={"item": updated},
        )

    except HTTPException as e:
        return _handle_http_exc_as_response(
            e, details={"item_id": str(item_id), "payload": updates, "detail": str(e.detail)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Optional: Update-note Endpoint (UPDATED, NOT_FOUND, INVALID)
# ==========================================================
@router.patch(
    "/{id:uuid}/note",
    response_class=UnicodeJSONResponse,
    # TODO: set response_model=UpdateNoteEnvelope
    # response_model=UpdateNoteEnvelope,
    response_model_exclude_none=True,
)
async def update_note_by_id(
    item_id: UUID,
    payload,  # TODO: type: UpdateNoteModel
    db: AsyncSession = Depends(get_db),
):
    """
    Use this when your entity has a separate note/text update endpoint.
    Remove this block if not needed.
    """
    try:
        # TODO: await update_note_service(item_id=item_id, body=payload)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"item_id": str(item_id)},
        )

    except HTTPException as e:
        return _handle_http_exc_as_response(
            e, details={"item_id": str(item_id), "detail": str(e.detail)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Optional: Action Endpoint (UPDATED, NOT_FOUND, INVALID)
# ==========================================================
@router.post(
    "/{id:uuid}/actions",
    response_class=UnicodeJSONResponse,
    # TODO: set response_model=ActionEnvelope
    # response_model=ActionEnvelope,
    response_model_exclude_none=True,
)
async def action_by_id(
    item_id: UUID,
    payload,  # TODO: type: ActionBodyModel
    db: AsyncSession = Depends(get_db),
):
    """
    Use this when you have a status/action endpoint (e.g. booking status action).
    Remove this block if not needed.
    """
    try:
        # TODO: result = await action_service(item_id=item_id, **payload.model_dump())
        result = None  # placeholder

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"result": result},
        )

    except HTTPException as e:
        return _handle_http_exc_as_response(
            e, details={"item_id": str(item_id), "detail": str(e.detail)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Optional: History Endpoint (RETRIEVED, EMPTY, NOT_FOUND)
# ==========================================================
@router.get(
    "/{id:uuid}/history",
    response_class=UnicodeJSONResponse,
    # TODO: set response_model=HistoryEnvelope
    # response_model=HistoryEnvelope,
    response_model_exclude_none=True,
)
async def history_by_id(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Use this when your entity has a history/log endpoint.
    Remove this block if not needed.
    """
    try:
        # TODO: data = await history_service(item_id=item_id)
        # items = getattr(data, "items", None) or []
        items = []  # placeholder

        if not items:
            return ResponseHandler.error(
                *_data_code("EMPTY", "EMPTY", "No data found"),
                details={"item_id": str(item_id)},
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"item_id": str(item_id), "items": items},
        )

    except HTTPException as e:
        return _handle_http_exc_as_response(
            e, details={"item_id": str(item_id), "detail": str(e.detail)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

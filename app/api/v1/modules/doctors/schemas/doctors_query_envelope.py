from app.api.v1.models._envelopes.base_envelopes import ErrorEnvelope, SuccessEnvelope

# Backward-compatible aliases
SuccessResponse = SuccessEnvelope
ErrorResponse = ErrorEnvelope

__all__ = [
    "SuccessEnvelope",
    "ErrorEnvelope",
    "SuccessResponse",
    "ErrorResponse",
]
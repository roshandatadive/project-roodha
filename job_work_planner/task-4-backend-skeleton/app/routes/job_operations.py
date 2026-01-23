"""
job_operations.py
-----------------
SCRUM 28 – Update Job Operation Status API

Responsibilities:
- Authentication
- RBAC
- Input validation
- Call service layer
- Return response

IMPORTANT:
- NO business logic here
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.core.job_operations_service import (
    update_job_operation_status,
)

# -------------------------------------------------------
# Router (MUST be defined BEFORE decorators)
# -------------------------------------------------------
router = APIRouter(
    prefix="/job-operations",
    tags=["Job Operations"]
)

# -------------------------------------------------------
# PATCH /job-operations/{job_operation_id}/status
# -------------------------------------------------------
@router.patch("/{job_operation_id}/status")
def update_operation_status(
    job_operation_id: str,
    payload: dict,
    request: Request,
):
    """
    Update job operation status (SCRUM 28)
    """

    # ---------------------------------------------------
    # 1. Authentication
    # ---------------------------------------------------
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    user = request.state.user
    role = user.get("role", "OPERATOR")

    # ---------------------------------------------------
    # 2. RBAC
    # ---------------------------------------------------
    if role not in {"OPERATOR", "SUPERVISOR", "OWNER"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    # ---------------------------------------------------
    # 3. Read payload
    # ---------------------------------------------------
    new_status = payload.get("status")
    quantity_completed = payload.get("quantity_completed")
    quantity_rejected = payload.get("quantity_rejected")
    rework_flag = payload.get("rework_flag", False)
    rework_note = payload.get("rework_note")
    override_sequence = payload.get("override_sequence", False)

    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status is required"
        )

    # ---------------------------------------------------
    # 4. Call service layer
    # ---------------------------------------------------
    try:
        updated_operation = update_job_operation_status(
            job_operation_id=job_operation_id,
            new_status=new_status,
            quantity_completed=quantity_completed,
            quantity_rejected=quantity_rejected,
            rework_flag=rework_flag,
            rework_note=rework_note,
            override_sequence=override_sequence,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    # ---------------------------------------------------
    # 5. Response
    # ---------------------------------------------------
    return updated_operation
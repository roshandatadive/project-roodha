# app/routes/planning.py

from fastapi import APIRouter, HTTPException, Request, Query, status
from app.core.planning_service import get_planning_calendar_service

router = APIRouter(
    prefix="/planning",
    tags=["Planning Calendar"]
)

@router.get("/")
def get_planning_calendar(
    request: Request,
    from_date: str | None = Query(None, description="YYYY-MM-DD"),
    to_date: str | None = Query(None, description="YYYY-MM-DD"),
    machine_id: str | None = Query(None),
    shift_id: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    GET /planning
    
    Returns operations grouped by machine → shift → date.
    Contract defined for Frontend Gantt / Calendar views.
    """
    
    # 1. Auth & Context
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    user = request.state.user
    tenant_id = user["tenant_id"]

    # 2. Call Service
    try:
        response = get_planning_calendar_service(
            tenant_id=tenant_id,
            from_date=from_date,
            to_date=to_date,
            machine_id=machine_id,
            shift_id=shift_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
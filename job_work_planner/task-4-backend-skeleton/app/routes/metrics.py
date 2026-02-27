# app/routes/metrics.py

from fastapi import APIRouter, HTTPException, Request, Query
from app.core.metrics_service import (
    get_wip_metrics_service,
    get_bottleneck_metrics_service,
    get_late_jobs_service
)

router = APIRouter(
    prefix="/metrics",
    tags=["Dashboard & Metrics"]
)

def _get_dashboard_user(request: Request):
    """Helper to enforce RBAC for dashboard access."""
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    user = request.state.user
    role = user.get("role")
    
    # Operators don't usually need the global analytics dashboard
    if role not in {"PLANNER", "SUPERVISOR", "ADMIN", "OWNER"}:
        raise HTTPException(status_code=403, detail="Forbidden: Dashboard access denied.")
        
    return user["tenant_id"]

# =======================================================
# GET /metrics/wip
# =======================================================
@router.get("/wip")
def get_wip_metrics(
    request: Request,
    from_date: str | None = Query(None, description="YYYY-MM-DD"),
    to_date: str | None = Query(None, description="YYYY-MM-DD")
):
    tenant_id = _get_dashboard_user(request)
    return {"wip_by_stage": get_wip_metrics_service(tenant_id, from_date, to_date)}

# =======================================================
# GET /metrics/bottlenecks
# =======================================================
@router.get("/bottlenecks")
def get_bottleneck_metrics(
    request: Request,
    from_date: str | None = Query(None, description="YYYY-MM-DD"),
    to_date: str | None = Query(None, description="YYYY-MM-DD")
):
    tenant_id = _get_dashboard_user(request)
    return {"bottlenecks": get_bottleneck_metrics_service(tenant_id, from_date, to_date)}

# =======================================================
# GET /metrics/late-jobs
# =======================================================
@router.get("/late-jobs")
def get_late_jobs_metrics(request: Request):
    tenant_id = _get_dashboard_user(request)
    return get_late_jobs_service(tenant_id)
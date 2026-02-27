# app/routes/system.py

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(
    tags=["System"]
)

# -------------------------------------------------------
# PUBLIC ENDPOINTS (No Auth Required)
# -------------------------------------------------------

@router.get("/health")
def health_check():
    """Health check for Load Balancers & Kubernetes."""
    return {
        "status": "ok",
        "service": "jobwork-backend"
    }

@router.get("/ready")
def readiness_check():
    """Readiness probe for traffic routing."""
    return {
        "status": "ready",
        "dependencies": {
            "database": "not_checked",
            "s3": "not_checked"
        }
    }

# -------------------------------------------------------
# PROTECTED ENDPOINTS
# -------------------------------------------------------

@router.get("/tenant/current")
def get_current_tenant(request: Request):
    """
    Returns current tenant context.
    Relying on JWTAuthMiddleware for request.state.user!
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = request.state.user

    # Mock tenant info (Later fetch this from a TENANTS_TABLE)
    tenant = {
        "tenant_id": user["tenant_id"],
        "tenant_name": "Demo Company Pvt Ltd",
        "plan": "trial"
    }

    return {
        "user": user,
        "tenant": tenant
    }
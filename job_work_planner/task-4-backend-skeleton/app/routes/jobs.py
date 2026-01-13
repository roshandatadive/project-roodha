"""
jobs.py
-------
Job APIs

RESPONSIBILITIES:
- Scrum 24: Create Job Header
- Scrum 25: Auto-generate Job Operations from Part Route

IMPORTANT DESIGN RULES:
- tenant_id NEVER comes from request payload
- tenant_id ALWAYS comes from JWT (request.state.user)
- Job operations are generated ONLY AFTER job header is created
- If operation creation fails → job is rolled back (atomic behavior)
"""

from fastapi import APIRouter, HTTPException, Request, status
from datetime import datetime
import uuid
import logging

# 🔗 Import Scrum 25 service
from app.core.job_operations_service import create_job_operations

# -------------------------------------------------------------------
# Router
# -------------------------------------------------------------------
router = APIRouter(prefix="/jobs", tags=["Jobs"])

# -------------------------------------------------------------------
# Logger (shared app logger)
# -------------------------------------------------------------------
logger = logging.getLogger("jobwork-backend")

# -------------------------------------------------------------------
# MOCK DATABASES (temporary – DB later)
# -------------------------------------------------------------------
JOBS_TABLE = {}  # job_id → job header

MOCK_CUSTOMERS = {
    "cust-1": {"tenant_id": "tenant-1"}
}

MOCK_PARTS = {
    "part-1": {"tenant_id": "tenant-1"}
}

ALLOWED_PRIORITY = {"LOW", "MEDIUM", "HIGH"}
ALLOWED_CREATOR_ROLES = {"OWNER", "SUPERVISOR"}

# -------------------------------------------------------------------
# POST /jobs
# -------------------------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_job(payload: dict, request: Request):
    """
    POST /jobs

    FLOW:
    1. Authenticate user
    2. Validate job header input (Scrum 24)
    3. Create job header
    4. Auto-generate job operations (Scrum 25)
    5. Return job + operations
    """

    # ---------------------------------------------------------------
    # 1. Authentication
    # ---------------------------------------------------------------
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = request.state.user
    tenant_id = user["tenant_id"]
    created_by = user["user_id"]
    role = user.get("role", "OWNER")

    # ---------------------------------------------------------------
    # 2. RBAC
    # ---------------------------------------------------------------
    if role not in ALLOWED_CREATOR_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden")

    # ---------------------------------------------------------------
    # 3. Read payload
    # ---------------------------------------------------------------
    customer_id = payload.get("customer_id")
    part_id = payload.get("part_id")
    quantity = payload.get("quantity")
    received_date = payload.get("received_date")
    due_date = payload.get("due_date")
    priority = payload.get("priority")

    # ---------------------------------------------------------------
    # 4. Validations (Scrum 24)
    # ---------------------------------------------------------------
    if not all([customer_id, part_id, quantity, received_date, due_date, priority]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be > 0")

    if priority not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail="Invalid priority")

    if due_date < received_date:
        raise HTTPException(status_code=400, detail="Invalid date range")

    if customer_id not in MOCK_CUSTOMERS or MOCK_CUSTOMERS[customer_id]["tenant_id"] != tenant_id:
        raise HTTPException(status_code=400, detail="Invalid customer")

    if part_id not in MOCK_PARTS or MOCK_PARTS[part_id]["tenant_id"] != tenant_id:
        raise HTTPException(status_code=400, detail="Invalid part")

    # ---------------------------------------------------------------
    # 5. Generate Job Header
    # ---------------------------------------------------------------
    job_id = str(uuid.uuid4())

    tenant_job_count = sum(
        1 for job in JOBS_TABLE.values()
        if job["tenant_id"] == tenant_id
    )

    job_number = f"JOB-{tenant_id.upper()}-{tenant_job_count + 1:04d}"

    now = datetime.utcnow().isoformat()

    job = {
        "job_id": job_id,
        "job_number": job_number,
        "customer_id": customer_id,
        "part_id": part_id,
        "tenant_id": tenant_id,
        "quantity": quantity,
        "received_date": received_date,
        "due_date": due_date,
        "priority": priority,
        "status": "NOT_STARTED",
        "created_by": created_by,
        "created_at": now,
        "updated_at": now,
    }

    # Persist job header
    JOBS_TABLE[job_id] = job

    # ---------------------------------------------------------------
    # 6. SCRUM 25 INTEGRATION (CRITICAL PART)
    # ---------------------------------------------------------------
    try:
        job_operations = create_job_operations(
            job_id=job_id,
            part_id=part_id,
            tenant_id=tenant_id
        )
    except Exception as e:
        # 🔥 Atomic rollback (required by Jira)
        JOBS_TABLE.pop(job_id, None)
        raise HTTPException(status_code=400, detail=str(e))

    # ---------------------------------------------------------------
    # 7. Audit logs
    # ---------------------------------------------------------------
    logger.info(
        "JOB_CREATED",
        extra={"job_id": job_id, "tenant_id": tenant_id}
    )

    logger.info(
        "JOB_ROUTE_CREATED",
        extra={"job_id": job_id, "tenant_id": tenant_id}
    )

    # ---------------------------------------------------------------
    # 8. Response (Scrum 24 + 25)
    # ---------------------------------------------------------------
    return {
        "job": job,
        "operations": job_operations
    }
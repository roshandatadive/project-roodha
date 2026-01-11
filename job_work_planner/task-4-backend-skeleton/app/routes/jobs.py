"""
jobs.py
--------
Job Header APIs (Scrum 24)
 
Handles ONLY:
- Job creation (job header)
- Validations
- Job number generation
- RBAC
- Audit logging
 
IMPORTANT:
- tenant_id is NOT taken from request payload
- tenant_id is derived from JWT (request.state.user)
"""
 
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import uuid
import logging
 
router = APIRouter(prefix="/jobs", tags=["Jobs"])
 
# -----------------------------
# Logger (Audit)
# -----------------------------
logger = logging.getLogger("jobwork-backend")
 
# -----------------------------
# MOCK DATABASES (temporary)
# -----------------------------
JOBS_TABLE = {}
 
MOCK_CUSTOMERS = {"cust-1": {"tenant_id": "tenant-1"}}
MOCK_PARTS = {"part-1": {"tenant_id": "tenant-1"}}
 
ALLOWED_PRIORITY = {"LOW", "MEDIUM", "HIGH"}
 
@router.post("/", status_code=201)
def create_job(payload: dict, request: Request):
    """
    POST /jobs
 
    Purpose:
    - Create job header ONLY (Scrum 24)
 
    Expected payload:
    {
        "customer_id": "cust-1",
        "part_id": "part-1",
        "quantity": 10,
        "received_date": "2025-01-01",
        "due_date": "2025-01-10",
        "priority": "HIGH"
    }
    """
 
    # -----------------------------
    # 1. Authentication check
    # -----------------------------
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
 
    user = request.state.user
    tenant_id = user["tenant_id"]
    created_by = user["user_id"]
    role = user.get("role", "OWNER")  # default mock
 
    # -----------------------------
    # 2. RBAC
    # -----------------------------
    if role == "OPERATOR":
        raise HTTPException(status_code=403, detail="Forbidden")
 
    # -----------------------------
    # 3. Read payload
    # -----------------------------
    customer_id = payload.get("customer_id")
    part_id = payload.get("part_id")
    quantity = payload.get("quantity")
    received_date = payload.get("received_date")
    due_date = payload.get("due_date")
    priority = payload.get("priority")
 
    # -----------------------------
    # 4. Validations
    # -----------------------------
    if not all([customer_id, part_id, quantity, received_date, due_date, priority]):
        raise HTTPException(status_code=400, detail="Missing required fields")
 
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
 
    if priority not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail="Invalid priority")
 
    if due_date < received_date:
        raise HTTPException(status_code=400, detail="Due date cannot be before received date")
 
    # -----------------------------
    # 5. Customer & Part validation (mock)
    # -----------------------------
    if customer_id not in MOCK_CUSTOMERS or MOCK_CUSTOMERS[customer_id]["tenant_id"] != tenant_id:
        raise HTTPException(status_code=400, detail="Invalid customer")
 
    if part_id not in MOCK_PARTS or MOCK_PARTS[part_id]["tenant_id"] != tenant_id:
        raise HTTPException(status_code=400, detail="Invalid part")
 
    # -----------------------------
    # 6. Generate job_id & job_number
    # -----------------------------
    job_id = str(uuid.uuid4())
    job_number = f"JOB-{tenant_id.upper()}-{len(JOBS_TABLE) + 1:04d}"
 
    # -----------------------------
    # 7. Create job record
    # -----------------------------
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
 
    JOBS_TABLE[job_id] = job
 
    # -----------------------------
    # 8. Audit log
    # -----------------------------
    logger.info("JOB_CREATED", extra={"job_id": job_id, "tenant_id": tenant_id})
 
    # -----------------------------
    # 9. Response
    # -----------------------------
    return job
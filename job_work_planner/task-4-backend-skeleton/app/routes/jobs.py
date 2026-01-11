"""
jobs.py
--------
Job Header APIs (Scrum 24)
 
This file handles ONLY:
- Job header creation
- Input validations
- Job number generation
- Tenant isolation
 
IMPORTANT:
- tenant_id is NOT taken from request payload
- tenant_id is derived from JWT (request.state.user)
- No job operations logic here (that is Scrum 25)
"""
 
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import uuid
 
# -----------------------------
# Router configuration
# -----------------------------
router = APIRouter(prefix="/jobs", tags=["Jobs"])
 
# -----------------------------
# MOCK DATABASE TABLES
# (Later these will be DynamoDB)
# -----------------------------
JOBS_TABLE = {}
 
CUSTOMERS_TABLE = {
    "cust-1": {
        "customer_id": "cust-1",
        "tenant_id": "tenant-1",
        "name": "Demo Customer"
    }
}
 
PARTS_TABLE = {
    "part-1": {
        "part_id": "part-1",
        "tenant_id": "tenant-1",
        "name": "Demo Part"
    }
}
 
ALLOWED_PRIORITY = {"LOW", "MEDIUM", "HIGH"}
 
# -----------------------------
# POST /jobs
# -----------------------------
@router.post("/", status_code=201)
def create_job(payload: dict, request: Request):
    """
    POST /jobs
 
    Purpose:
    - Create a Job HEADER only (Scrum 24)
 
    Expected payload:
    {
        "customer_id": "cust-1",
        "part_id": "part-1",
        "quantity": 10,
        "received_date": "2025-01-01",
        "due_date": "2025-01-10",
        "priority": "HIGH"
    }
 
    Notes:
    - tenant_id comes from JWT
    - created_by comes from JWT
    """
 
    # -----------------------------
    # 1. Extract user from JWT
    # -----------------------------
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
 
    user = request.state.user
    tenant_id = user["tenant_id"]
    created_by = user["user_id"]
 
    # -----------------------------
    # 2. Read payload fields
    # -----------------------------
    customer_id = payload.get("customer_id")
    part_id = payload.get("part_id")
    quantity = payload.get("quantity")
    received_date = payload.get("received_date")
    due_date = payload.get("due_date")
    priority = payload.get("priority")
 
    # -----------------------------
    # 3. Basic validations
    # -----------------------------
    if not all([customer_id, part_id, quantity, received_date, due_date, priority]):
        raise HTTPException(status_code=400, detail="Missing required fields")
 
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
 
    if priority not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail="Invalid priority")
 
    if due_date < received_date:
        raise HTTPException(
            status_code=400,
            detail="Due date cannot be before received date"
        )
 
    # -----------------------------
    # 4. Validate customer
    # -----------------------------
    customer = CUSTOMERS_TABLE.get(customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found")
 
    if customer["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Customer does not belong to tenant")
 
    # -----------------------------
    # 5. Validate part
    # -----------------------------
    part = PARTS_TABLE.get(part_id)
    if not part:
        raise HTTPException(status_code=400, detail="Part not found")
 
    if part["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Part does not belong to tenant")
 
    # -----------------------------
    # 6. Generate IDs
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
        "updated_at": now
    }
 
    JOBS_TABLE[job_id] = job
 
    # -----------------------------
    # 8. Response
    # -----------------------------
    return job
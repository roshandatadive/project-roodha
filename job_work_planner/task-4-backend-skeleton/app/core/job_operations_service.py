"""
job_operations_service.py
-------------------------
 
This file contains business logic for creating job operations
from a Part's default operation route.
 
IMPORTANT:
- This is NOT an API
- This is a service function
- It will be called when a Job is created
"""
 
from typing import List, Dict
from uuid import uuid4
 
 
# -----------------------------
# Mock database tables (TEMP)
# -----------------------------
 
# Simulating Part table
PARTS_TABLE = {
    "part-1": {
        "part_id": "part-1",
        "tenant_id": "tenant-1",
        "default_operations_route": ["op-cut", "op-drill", "op-paint"]
    }
}
 
# Simulating Operations master table
OPERATIONS_TABLE = {
    "op-cut": {"operation_id": "op-cut", "name": "Cut"},
    "op-drill": {"operation_id": "op-drill", "name": "Drill"},
    "op-paint": {"operation_id": "op-paint", "name": "Paint"},
}
 
# Simulating Job Operations table
JOB_OPERATIONS_TABLE: List[Dict] = {}




# -------------------------------------------------------
# Route Validation Logic (STEP 2)
# -------------------------------------------------------
 
def validate_part_route(part_id: str, tenant_id: str):
    """
    Validates the default operation route for a given Part.
 
    What this function guarantees:
    1. Part exists
    2. Route is not empty
    3. All operation IDs in the route exist
    """
 
    # 1️⃣ Fetch part
    part = PARTS_TABLE.get(part_id)
 
    if not part:
        raise ValueError("Part does not exist")
 
    if part["tenant_id"] != tenant_id:
        raise ValueError("Part does not belong to tenant")
 
    # 2️⃣ Read route
    route = part.get("default_operations_route")
 
    if not route or len(route) == 0:
        raise ValueError("Part has no operation route defined")
 
    # 3️⃣ Validate each operation
    for op_id in route:
        if op_id not in OPERATIONS_TABLE:
            raise ValueError(f"Invalid operation in route: {op_id}")
 
    # 4️⃣ If everything is valid, return route
    return route



# -------------------------------------------------------
# Job Operation Creation Logic (STEP 3 - ATOMIC)
# -------------------------------------------------------
 
def create_job_operations(job_id: str, part_id: str, tenant_id: str):
    """
    Creates job_operations for a job based on Part route.
 
    Atomic guarantee:
    - If any operation creation fails, rollback everything.
    """
 
    created_operations = []
 
    try:
        # 1️⃣ Validate route first
        route = validate_part_route(part_id, tenant_id)
 
        # 2️⃣ Create job operations in order
        for index, op_id in enumerate(route):
            job_operation_id = f"{job_id}-{op_id}"
 
            job_operation = {
                "job_operation_id": job_operation_id,
                "job_id": job_id,
                "operation_id": op_id,
                "sequence_number": index + 1,
                "status": "READY" if index == 0 else "NOT_STARTED"
            }
 
            # Simulate persistence
            JOB_OPERATIONS_TABLE[job_operation_id] = job_operation
            created_operations.append(job_operation_id)
 
        return created_operations
 
    except Exception as e:
        # 3️⃣ ROLLBACK (CRITICAL)
        for job_op_id in created_operations:
            JOB_OPERATIONS_TABLE.pop(job_op_id, None)
 
        raise e



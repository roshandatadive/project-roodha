"""
job_operations_service.py
-------------------------

SCRUM 25 – Auto Generate Job Operations

Responsibilities:
- Read Part default operation route
- Validate route + tenant isolation
- Create job_operations atomically
- Rollback on failure
- Write audit log entry: JOB_ROUTE_CREATED

IMPORTANT:
- This is a SERVICE, not an API
"""

from typing import List, Dict
import logging

logger = logging.getLogger("jobwork-backend")

# -----------------------------
# MOCK DATABASE TABLES
# (Replace with DynamoDB later)
# -----------------------------

PARTS_TABLE = {
    "part-1": {
        "part_id": "part-1",
        "tenant_id": "tenant-1",
        "default_operations_route": ["op-cut", "op-drill", "op-paint"],
    }
}

OPERATIONS_TABLE = {
    "op-cut": {"operation_id": "op-cut", "name": "Cut"},
    "op-drill": {"operation_id": "op-drill", "name": "Drill"},
    "op-paint": {"operation_id": "op-paint", "name": "Paint"},
}

# job_operation_id -> record
JOB_OPERATIONS_TABLE: Dict[str, Dict] = {}

# -------------------------------------------------------
# STEP 1: Route Validation
# -------------------------------------------------------

def validate_part_route(part_id: str, tenant_id: str) -> List[str]:
    """
    Validates Part default operation route.

    Guarantees:
    - Part exists
    - Part belongs to tenant
    - Route is not empty
    - All operation IDs exist
    """

    part = PARTS_TABLE.get(part_id)
    if not part:
        raise ValueError("Part does not exist")

    if part["tenant_id"] != tenant_id:
        raise ValueError("Part does not belong to tenant")

    route = part.get("default_operations_route")
    if not route:
        raise ValueError("Part has no operation route defined")

    for op_id in route:
        if op_id not in OPERATIONS_TABLE:
            raise ValueError(f"Invalid operation in route: {op_id}")

    return route


# -------------------------------------------------------
# STEP 2: Job Operation Creation (ATOMIC)
# -------------------------------------------------------

def create_job_operations(job_id: str, part_id: str, tenant_id: str) -> List[Dict]:
    """
    Creates job operations from part route.

    Atomic guarantee:
    - If ANY step fails → rollback everything
    """

    created_operation_ids = []

    try:
        route = validate_part_route(part_id, tenant_id)

        for index, op_id in enumerate(route):
            job_operation_id = f"{job_id}-{op_id}"

            job_operation = {
                "job_operation_id": job_operation_id,
                "job_id": job_id,
                "operation_id": op_id,
                "sequence_number": index + 1,
                "status": "READY" if index == 0 else "NOT_STARTED",
            }

            JOB_OPERATIONS_TABLE[job_operation_id] = job_operation
            created_operation_ids.append(job_operation_id)

        # ✅ AUDIT LOG (Jira requirement)
        logger.info(
            "JOB_ROUTE_CREATED",
            extra={"job_id": job_id, "tenant_id": tenant_id},
        )

        return created_operation_ids

    except Exception as exc:
        # 🔴 ROLLBACK (CRITICAL)
        for op_id in created_operation_ids:
            JOB_OPERATIONS_TABLE.pop(op_id, None)

        raise exc


# -------------------------------------------------------
# STEP 3: Read Operations for a Job
# -------------------------------------------------------

def get_job_operations(job_id: str) -> List[Dict]:
    """
    Returns job operations ordered by sequence_number.
    Used by GET /jobs/{job_id}
    """

    operations = [
        op for op in JOB_OPERATIONS_TABLE.values()
        if op["job_id"] == job_id
    ]

    return sorted(operations, key=lambda x: x["sequence_number"])
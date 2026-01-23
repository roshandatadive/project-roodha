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
from datetime import datetime
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


# -------------------------------------------------------
# SCRUM 28: Operation Status Constants
# -------------------------------------------------------

OP_STATUS_NOT_STARTED = "NOT_STARTED"
OP_STATUS_READY = "READY"
OP_STATUS_IN_PROGRESS = "IN_PROGRESS"
OP_STATUS_ON_HOLD = "ON_HOLD"
OP_STATUS_COMPLETED = "COMPLETED"
OP_STATUS_CANCELLED = "CANCELLED"


# -------------------------------------------------------
# SCRUM 28: Allowed Status Transitions (State Machine)
# -------------------------------------------------------

ALLOWED_STATUS_TRANSITIONS = {
    OP_STATUS_NOT_STARTED: {OP_STATUS_IN_PROGRESS, OP_STATUS_CANCELLED},
    OP_STATUS_READY: {OP_STATUS_IN_PROGRESS},
    OP_STATUS_IN_PROGRESS: {OP_STATUS_COMPLETED, OP_STATUS_ON_HOLD},
    OP_STATUS_ON_HOLD: {OP_STATUS_IN_PROGRESS},
    OP_STATUS_COMPLETED: set(),
    OP_STATUS_CANCELLED: set(),
}




def is_valid_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validates whether a status change is allowed
    based on the defined state machine.
    """
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
    return new_status in allowed





# -------------------------------------------------------
# SCRUM 28: Update Job Operation Status (Service Logic)
# -------------------------------------------------------

def update_job_operation_status(
    job_operation_id: str,
    new_status: str,
    *,
    quantity_completed: int | None = None,
    quantity_rejected: int | None = None,
    rework_flag: bool = False,
    rework_note: str | None = None,
    override_sequence: bool = False,
):
    """
    Updates the status of a job operation while enforcing:
    - State machine rules
    - Sequence constraints
    - Quantity validations
    - Timestamp tracking
    - Parent job status updates

    This is SERVICE logic (called by API later).
    """

    # ---------------------------------------------------
    # 1. Fetch job operation
    # ---------------------------------------------------
    job_op = JOB_OPERATIONS_TABLE.get(job_operation_id)
    if not job_op:
        raise ValueError("Job operation not found")

    current_status = job_op["status"]

    # ---------------------------------------------------
    # 2. Validate state transition
    # ---------------------------------------------------
    if not is_valid_status_transition(current_status, new_status):
        raise ValueError(
            f"Invalid status transition: {current_status} → {new_status}"
        )

   



# ---------------------------------------------------
    # 3. Sequence enforcement (SCRUM 28)
    # ---------------------------------------------------
    if new_status == OP_STATUS_IN_PROGRESS and not override_sequence:
        job_id = job_op["job_id"]
        seq = job_op["sequence_number"]

        # If this is not the first operation, check previous op
        if seq > 1:
            prev_ops = [
                op for op in JOB_OPERATIONS_TABLE.values()
                if op["job_id"] == job_id
                and op["sequence_number"] == seq - 1
            ]

            if not prev_ops:
                raise ValueError("Previous operation not found")

            prev_op = prev_ops[0]

            if prev_op["status"] != OP_STATUS_COMPLETED:
                raise ValueError(
                    "Previous operation must be COMPLETED before starting this one"
                )








# ---------------------------------------------------
    # STEP 4: Quantity & Completion Validations
    # ---------------------------------------------------
    if new_status == OP_STATUS_COMPLETED:

        if quantity_completed is None:
            raise ValueError(
                "quantity_completed is required when completing an operation"
            )

        if quantity_completed < 0:
            raise ValueError("quantity_completed cannot be negative")

        if quantity_rejected is None:
            quantity_rejected = 0

        if quantity_rejected < 0:
            raise ValueError("quantity_rejected cannot be negative")

        # 🔒 Job quantity enforcement
        # (Job qty will come from JOBS_TABLE later via API layer)
        job_qty = job_op.get("job_quantity")  # placeholder for now

        if job_qty is not None:
            if quantity_completed > job_qty:
                raise ValueError("quantity_completed exceeds job quantity")

            if (quantity_completed + quantity_rejected) > job_qty:
                raise ValueError(
                    "completed + rejected quantity exceeds job quantity"
                )

        # 🔁 Rework validation
        if rework_flag and not rework_note:
            raise ValueError("rework_note is required when rework_flag is true")







# ---------------------------------------------------
    # STEP 5: Timestamp handling & status mutation
    # ---------------------------------------------------

    now = datetime.utcnow().isoformat()

    # When operation starts
    if new_status == OP_STATUS_IN_PROGRESS:
        if not job_op.get("actual_start_time"):
            job_op["actual_start_time"] = now

    # When operation completes
    if new_status == OP_STATUS_COMPLETED:
        job_op["actual_end_time"] = now

        # Persist quantities
        job_op["quantity_completed"] = quantity_completed
        job_op["quantity_rejected"] = quantity_rejected or 0

        if rework_flag:
            job_op["rework_flag"] = True
            job_op["rework_note"] = rework_note

    # Update status (single source of truth)
    job_op["status"] = new_status





# ---------------------------------------------------
    # STEP 6: Update parent job status
    # ---------------------------------------------------

    from app.routes.jobs import JOBS_TABLE  # mock import (temporary)

    job_id = job_op["job_id"]
    job = JOBS_TABLE.get(job_id)

    if not job:
        raise ValueError("Parent job not found")

    # Fetch all operations for this job
    all_ops = [
        op for op in JOB_OPERATIONS_TABLE.values()
        if op["job_id"] == job_id
    ]

    # If any operation is IN_PROGRESS → job IN_PROGRESS
    if any(op["status"] == OP_STATUS_IN_PROGRESS for op in all_ops):
        job["status"] = "IN_PROGRESS"

    # If ALL operations are COMPLETED → job COMPLETED
    elif all(op["status"] == OP_STATUS_COMPLETED for op in all_ops):
        job["status"] = "COMPLETED"

    # Otherwise → NOT_STARTED
    else:
        job["status"] = "NOT_STARTED"

    job["updated_at"] = now





# ---------------------------------------------------
    # STEP 7: Audit logging + response
    # ---------------------------------------------------

    logger.info(
        "OP_STATUS_CHANGED",
        extra={
            "event": "OP_STATUS_CHANGED",
            "job_operation_id": job_operation_id,
            "job_id": job_op["job_id"],
            "old_status": current_status,
            "new_status": new_status,
            "quantity_completed": job_op.get("quantity_completed"),
            "quantity_rejected": job_op.get("quantity_rejected"),
            "rework_flag": job_op.get("rework_flag", False),
        },
    )

    # Return updated operation
    return job_op
















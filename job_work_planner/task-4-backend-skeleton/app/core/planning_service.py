# app/core/planning_service.py

from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger("jobwork-backend")

# Import mock tables
from app.db.mock_db import JOBS_TABLE, JOB_OPERATIONS_TABLE, OPERATIONS_TABLE
def get_planning_calendar_service(
    *,
    tenant_id: str,
    from_date: str | None = None,
    to_date: str | None = None,
    machine_id: str | None = None,
    shift_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    """
    Builds a planner-friendly aggregated schedule.
    """
    # ---------------------------------------------------
    # 1. Fetch & Filter Operations
    # ---------------------------------------------------
    filtered_ops = []

    for op in JOB_OPERATIONS_TABLE.values():
        if op.get("tenant_id") != tenant_id:
            continue
            
        # Only include planned operations
        if not op.get("machine_id") or not op.get("planned_start_date"):
            continue

        if machine_id and op.get("machine_id") != machine_id:
            continue

        if shift_id and op.get("shift_id") != shift_id:
            continue

        if status and op.get("status") != status:
            continue

        # Date range filtering (Overlaps with from_date -> to_date)
        op_start = op["planned_start_date"][:10]  # Get YYYY-MM-DD
        op_end = op["planned_end_date"][:10] if op.get("planned_end_date") else op_start
        
        if from_date and op_end < from_date:
            continue
        if to_date and op_start > to_date:
            continue

        filtered_ops.append(op)

    # ---------------------------------------------------
    # 2. Sort & Paginate (Sort by start date)
    # ---------------------------------------------------
    filtered_ops.sort(key=lambda x: (x["planned_start_date"], x.get("sequence_number", 0)))
    
    total_count = len(filtered_ops)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_ops = filtered_ops[start_idx:end_idx]

    # ---------------------------------------------------
    # 3. Enrich & Group (Machine -> Shift -> Date -> Ops)
    # ---------------------------------------------------
    # Using nested defaultdicts for grouping
    calendar = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for op in paginated_ops:
        job = JOBS_TABLE.get(op["job_id"], {})
        op_master = OPERATIONS_TABLE.get(op["operation_id"], {})

        op_date = op["planned_start_date"][:10]
        m_id = op["machine_id"]
        s_id = op["shift_id"]

        # Build the enriched DTO required by the Acceptance Criteria
        enriched_op = {
            "job_operation_id": op["job_operation_id"],
            "job_id": op["job_id"],
            "job_number": job.get("job_number", "UNKNOWN"),
            "op_name": op_master.get("name", op["operation_id"]),
            "status": op["status"],
            "planned_qty": job.get("quantity", 0),  # Job planned qty
            "due_date": job.get("due_date"),
            "priority": job.get("priority"),
            "sequence_number": op["sequence_number"]
        }

        calendar[m_id][s_id][op_date].append(enriched_op)

    # Convert defaultdict to standard dict for clean JSON serialization
    grouped_data = {
        m: {
            s: dict(dates) for s, dates in shifts.items()
        } for m, shifts in calendar.items()
    }

    return {
        "data": grouped_data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    }
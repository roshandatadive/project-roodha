# app/core/metrics_service.py

from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger("jobwork-backend")

from app.db.mock_db import JOBS_TABLE, JOB_OPERATIONS_TABLE, MACHINES_TABLE

# -------------------------------------------------------
# 1. WIP by Stage
# -------------------------------------------------------
def get_wip_metrics_service(tenant_id: str, from_date: str | None = None, to_date: str | None = None) -> list:
    """
    Calculates Work-In-Progress (WIP) counts per operation stage.
    WIP = Operations that are currently active (READY, IN_PROGRESS, PAUSED).
    """
    wip_counts = defaultdict(int)

    for op in JOB_OPERATIONS_TABLE.values():
        if op.get("tenant_id") != tenant_id:
            continue
            
        # Optional: Date filtering based on planned start
        if from_date or to_date:
            start = op.get("planned_start_date", "")[:10]
            if from_date and start < from_date: continue
            if to_date and start > to_date: continue

        if op["status"] in {"READY", "IN_PROGRESS", "PAUSED"}:
            wip_counts[op["operation_id"]] += 1

    # Format for charts (e.g., Recharts or Chart.js)
    return [{"stage": stage, "count": count} for stage, count in wip_counts.items()]


# -------------------------------------------------------
# 2. Bottleneck Machines
# -------------------------------------------------------
def get_bottleneck_metrics_service(tenant_id: str, from_date: str | None = None, to_date: str | None = None) -> list:
    """
    Identifies machines with the highest backlog of operations.
    """
    machine_load = defaultdict(int)

    for op in JOB_OPERATIONS_TABLE.values():
        if op.get("tenant_id") != tenant_id:
            continue
            
        machine_id = op.get("machine_id")
        if not machine_id:
            continue # Skip unplanned operations

        # Backlog = anything not completed or cancelled
        if op["status"] not in {"COMPLETED", "CANCELLED"}:
            
            if from_date or to_date:
                start = op.get("planned_start_date", "")[:10]
                if from_date and start < from_date: continue
                if to_date and start > to_date: continue

            machine_load[machine_id] += 1

    # Format and sort (highest load first)
    bottlenecks = [
        {
            "machine_id": m_id, 
            "machine_name": MACHINES_TABLE.get(m_id, {}).get("machine_id", m_id),
            "pending_operations": count
        } 
        for m_id, count in machine_load.items()
    ]
    bottlenecks.sort(key=lambda x: x["pending_operations"], reverse=True)
    
    return bottlenecks


# -------------------------------------------------------
# 3. Late Jobs
# -------------------------------------------------------
def get_late_jobs_service(tenant_id: str) -> dict:
    """
    Returns jobs that have passed their due date but are not completed.
    """
    today = datetime.utcnow().date().isoformat()
    late_jobs = []

    for job in JOBS_TABLE.values():
        if job.get("tenant_id") != tenant_id:
            continue
            
        if job["status"] != "COMPLETED" and job["due_date"] < today:
            late_jobs.append({
                "job_id": job["job_id"],
                "job_number": job["job_number"],
                "customer_id": job["customer_id"],
                "due_date": job["due_date"],
                "priority": job["priority"],
                "status": job["status"]
            })

    # Sort by how late they are (oldest due date first)
    late_jobs.sort(key=lambda x: x["due_date"])

    return {
        "total_late": len(late_jobs),
        "jobs": late_jobs
    }
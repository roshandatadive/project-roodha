# app/db/mock_db.py
"""
Centralized Mock Database
Prevents circular imports between routers and services.
"""
from typing import Dict, List

# -----------------------------
# MOCK DATABASE TABLES
# -----------------------------
JOBS_TABLE: Dict[str, Dict] = {}
JOB_OPERATIONS_TABLE: Dict[str, Dict] = {}
JOB_OPERATION_PRODUCTION_TABLE: Dict[str, List[Dict]] = {}
JOB_OPERATION_RESCHEDULE_TABLE: Dict[str, List[Dict]] = {}

MACHINES_TABLE = {
    "machine-1": {"machine_id": "machine-1", "tenant_id": "tenant-1"},
    "machine-2": {"machine_id": "machine-2", "tenant_id": "tenant-1"},
}

SHIFTS_TABLE = {
    "shift-A": {"shift_id": "shift-A", "tenant_id": "tenant-1"},
    "shift-B": {"shift_id": "shift-B", "tenant_id": "tenant-1"},
}

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

MOCK_CUSTOMERS = {
    "cust-1": {"tenant_id": "tenant-1"}
}
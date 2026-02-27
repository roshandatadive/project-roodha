# app/core/audit_service.py

from datetime import datetime
import uuid
import logging

logger = logging.getLogger("jobwork-backend")

# ---------------------------------------------------------
# MOCK DATABASE (Append-Only for Immutability)
# ---------------------------------------------------------
# List of dicts representing audit records
AUDIT_LOGS_TABLE = []

def log_audit_event(
    tenant_id: str,
    entity_type: str,  # 'JOB' or 'JOB_OPERATION'
    entity_id: str,
    action: str,       # e.g., 'CREATED', 'STATUS_CHANGED', 'PLANNED'
    user_id: str,
    before: dict | None = None,
    after: dict | None = None,
) -> dict:
    """
    Writes an immutable audit record.
    """
    audit_record = {
        "audit_id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "before": before or {},
        "after": after or {},
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Append-only (Immutability enforced by lack of UPDATE/DELETE methods)
    AUDIT_LOGS_TABLE.append(audit_record)
    
    # Also dump to stdout/logger for infrastructure logging (CloudWatch/Datadog)
    logger.info(f"AUDIT | {entity_type} | {action} | User: {user_id}")
    
    return audit_record


def get_audit_trail(tenant_id: str, entity_type: str, entity_id: str) -> list:
    """
    Retrieves the audit trail, strictly enforcing tenant isolation.
    """
    trail = [
        entry for entry in AUDIT_LOGS_TABLE
        if entry["tenant_id"] == tenant_id
        and entry["entity_type"] == entity_type
        and entry["entity_id"] == entity_id
    ]
    
    # Sort descending (newest first)
    trail.sort(key=lambda x: x["timestamp"], reverse=True)
    return trail
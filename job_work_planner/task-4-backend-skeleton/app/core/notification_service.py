# app/core/notification_service.py

import uuid
from datetime import datetime
import logging

logger = logging.getLogger("jobwork-backend")

# MOCK DB: notification_id -> record
NOTIFICATIONS_TABLE = {}

def create_notification(
    tenant_id: str, 
    user_id: str | None,  # If None, broadcasts to all Supervisors in tenant
    notif_type: str,      # 'READY', 'CONFLICT', 'DELAY'
    message: str, 
    entity_ref: str
) -> dict:
    """
    Creates an in-app notification record.
    """
    notif_id = str(uuid.uuid4())
    notification = {
        "notification_id": notif_id,
        "tenant_id": tenant_id,
        "user_id": user_id, 
        "type": notif_type,
        "message": message,
        "entity_reference": entity_ref,
        "is_read": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    NOTIFICATIONS_TABLE[notif_id] = notification
    
    logger.info(f"NOTIFICATION_CREATED | Type: {notif_type} | Ref: {entity_ref}")
    return notification


def get_user_notifications(tenant_id: str, user_id: str, unread_only: bool = False) -> list:
    """
    Fetches notifications for a user (and tenant-wide broadcasts).
    """
    user_notifs = [
        n for n in NOTIFICATIONS_TABLE.values()
        if n["tenant_id"] == tenant_id and (n["user_id"] == user_id or n["user_id"] is None)
    ]
    
    if unread_only:
        user_notifs = [n for n in user_notifs if not n["is_read"]]
        
    user_notifs.sort(key=lambda x: x["created_at"], reverse=True)
    return user_notifs


def mark_notification_read(notification_id: str, tenant_id: str) -> dict:
    """
    Marks a specific notification as read.
    """
    notif = NOTIFICATIONS_TABLE.get(notification_id)
    if not notif:
        raise ValueError("Notification not found")
        
    if notif["tenant_id"] != tenant_id:
        raise ValueError("Unauthorized access to notification")
        
    notif["is_read"] = True
    notif["read_at"] = datetime.utcnow().isoformat()
    return notif
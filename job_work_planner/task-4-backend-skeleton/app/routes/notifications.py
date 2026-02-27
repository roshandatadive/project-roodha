# app/routes/notifications.py

from fastapi import APIRouter, HTTPException, Request, Query, status
from app.core.notification_service import get_user_notifications, mark_notification_read

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

@router.get("/")
def get_notifications(
    request: Request,
    unread_only: bool = Query(False)
):
    """
    Fetch in-app notifications for the logged-in user.
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    user = request.state.user
    
    notifs = get_user_notifications(
        tenant_id=user["tenant_id"], 
        user_id=user["user_id"],
        unread_only=unread_only
    )
    
    return {"notifications": notifs, "unread_count": sum(1 for n in notifs if not n["is_read"])}


@router.patch("/{notification_id}/read")
def mark_as_read(notification_id: str, request: Request):
    """
    Mark a notification as read.
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    try:
        updated = mark_notification_read(
            notification_id=notification_id, 
            tenant_id=request.state.user["tenant_id"]
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
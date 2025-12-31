"""
auth.py
--------
All authentication-related APIs live here.
 
Right now this is a SKELETON.
Real JWT validation will be added later.
"""
 
from fastapi import APIRouter, Header, HTTPException
 
# Create a router object
# Router = group of APIs
router = APIRouter()
 
@router.get("/me")
def get_current_user(authorization: str | None = Header(default=None)):
    """
    GET /me
    -------
    Purpose:
    - Check if request has JWT token
    - If token exists, allow request
    - Later: validate token with Cognito
 
    Header expected:
    Authorization: Bearer <JWT_TOKEN>
    """
 
    # 1️⃣ Check if Authorization header is missing
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
 
    # 2️⃣ Check correct format: Bearer <token>
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )
 
    # 3️⃣ Extract token (no validation yet)
    token = authorization.replace("Bearer ", "")
 
    # ⚠️ IMPORTANT:
    # We are NOT validating JWT signature yet.
    # This task is only structure + flow.
 
    return {
        "message": "JWT received successfully",
        "user": {
            "id": "mock-user-id",
            "email": "mock.user@jobwork.com"
        }
    }
 
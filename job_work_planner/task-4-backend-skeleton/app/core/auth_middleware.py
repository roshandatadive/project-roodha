"""
auth_middleware.py
------------------
Mock JWT authentication middleware.
 
Responsibilities:
- Allow /health without auth
- Require Authorization header for all other routes
- Attach user + tenant context to request.state
"""
 
from fastapi import Request, HTTPException
 
class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app
 
    async def __call__(self, request: Request, call_next):
        # Public endpoint
        if request.url.path == "/health":
            return await call_next(request)
 
        auth_header = request.headers.get("Authorization")
 
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")
 
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid Authorization header")
 
        token = auth_header.replace("Bearer ", "")
 
        # -----------------------------
        # MOCK JWT DECODE (for now)
        # -----------------------------
        # In real life:
        # - Verify signature with Cognito JWKs
        # - Validate expiry, issuer, audience
        # -----------------------------
 
        request.state.user = {
            "user_id": "mock-user-id",
            "email": "mock.user@jobwork.com",
            "tenant_id": "tenant-1",     # ✅ REQUIRED FIX
            "role": "OWNER"              # needed later for RBAC
        }
 
        response = await call_next(request)
        return response
 
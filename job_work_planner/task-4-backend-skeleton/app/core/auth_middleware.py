"""
auth_middleware.py
------------------
This file contains JWT authentication middleware.
 
What this middleware does:
1. Runs BEFORE every API request
2. Skips public endpoints like /health
3. Validates Authorization header
4. Rejects invalid or missing tokens
5. Attaches user info to request.state
"""
 
from fastapi import Request
from fastapi.responses import JSONResponse
 
 
class JWTAuthMiddleware:
    """
    This middleware acts like a SECURITY GUARD.
 
    Every request must pass through this guard
    before reaching any API route.
    """
 
    def __init__(self, app):
        self.app = app
 
    async def __call__(self, request: Request, call_next):
        """
        This function is automatically called for every request.
        """
 
        # 1️⃣ Allow PUBLIC endpoints without JWT
        if request.url.path in ["/health"]:
            return await call_next(request)
 
        # 2️⃣ Read Authorization header
        auth_header = request.headers.get("Authorization")
 
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing"},
            )
 
        # 3️⃣ Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid Authorization header format"},
            )
 
        # 4️⃣ Extract token
        token = auth_header.replace("Bearer ", "")
 
        # 5️⃣ MOCK token validation (Cognito will come later)
        if token == "" or token == "invalid":
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )
 
        # 6️⃣ Attach user info to request (DOWNSTREAM USE)
        request.state.user = {
            "user_id": "mock-user-id",
            "email": "mock.user@jobwork.com",
        }
 
        # 7️⃣ Allow request to proceed
        response = await call_next(request)
        return response
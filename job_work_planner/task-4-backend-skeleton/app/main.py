"""
main.py
-------
Application entry point.
Registers middleware and API routes.
"""

from fastapi import FastAPI

# Routers
from app.routes import system, auth, jobs

# Middleware
from app.core.auth_middleware import JWTAuthMiddleware

# ---------------------------------------------------------
# Create FastAPI app
# ---------------------------------------------------------
app = FastAPI(title="JobWork Backend Skeleton")

# ---------------------------------------------------------
# Register middleware (CORRECT WAY)
# ---------------------------------------------------------
app.add_middleware(JWTAuthMiddleware)

# ---------------------------------------------------------
# Register routes
# ---------------------------------------------------------
app.include_router(system.router)
app.include_router(auth.router)
app.include_router(jobs.router)
from fastapi import FastAPI
 
# Import system routes (health, ready, me, tenant)
from app.routes import system,auth
 
# Create FastAPI application
app = FastAPI(title="JobWork Backend Skeleton")
 
# Register system routes
app.include_router(system.router)
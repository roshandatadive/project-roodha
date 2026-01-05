from fastapi import FastAPI
from app.routes import system, auth
from app.core.auth_middleware import JWTAuthMiddleware
 
# Create FastAPI app
app = FastAPI(title="JobWork Backend Skeleton")
 
# Register middleware
app.middleware("http")(JWTAuthMiddleware(app))
 
# Register routes
app.include_router(system.router)
app.include_router(auth.router)
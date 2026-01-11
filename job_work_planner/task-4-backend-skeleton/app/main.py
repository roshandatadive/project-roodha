from fastapi import FastAPI

# Import routes

from app.routes import system, auth, jobs

# Import middleware

from app.core.auth_middleware import JWTAuthMiddleware

# Create FastAPI app

app = FastAPI(title="JobWork Backend Skeleton")

# Register JWT middleware (applies to all requests)

app.middleware("http")(JWTAuthMiddleware(app))

# Register routes

app.include_router(system.router)

app.include_router(auth.router)

app.include_router(jobs.router)
 
from fastapi import FastAPI
 
# Import routes
from app.routes import system, auth, jobs
 
# Import middleware
from app.core.auth_middleware import JWTAuthMiddleware
 
# Create FastAPI app
app = FastAPI(title="JobWork Backend Skeleton")
 
# Register JWT middleware (applies to all requests)
app.middleware("http")(JWTAuthMiddleware(app))
 
# Register routes
app.include_router(system.router)
app.include_router(auth.router)
app.include_router(jobs.router)
 
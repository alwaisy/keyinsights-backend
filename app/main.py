import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.middleware.logging import logging_middleware
from app.middleware.rate_limit import rate_limit_middleware

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# CORS middleware with environment-based configuration
origins = (
    ["*"] if settings.DEBUG else [
        "https://keyinsights-frontend.vercel.app",
        # Add other production domains here
    ]
)

allow_methods = ["*"] if settings.DEBUG else ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
allow_headers = ["*"] if settings.DEBUG else [
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "Accept",
    "Origin",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset"
    ],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Rate limiting middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

# Add logging middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Create the scheduled tasks module (app/tasks/scheduled.py)
# with the code from Step 3 in the previous response

# Create a lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services, background tasks, etc.
    # Import here to avoid circular imports
    from app.tasks.scheduled import schedule_tasks
    # Start scheduled tasks in the background
    task = asyncio.create_task(schedule_tasks())

    yield  # This is where the application runs

    # Shutdown: Clean up resources
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        # Task was cancelled, which is expected
        pass


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "YouTube Insights API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)

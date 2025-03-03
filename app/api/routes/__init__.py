from fastapi import APIRouter
from app.api.routes import transcript, insights, combined, status

api_router = APIRouter()
api_router.include_router(transcript.router, prefix="/transcript", tags=["Transcript"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(combined.router, prefix="/combined", tags=["Combined"])
api_router.include_router(status.router, prefix="/status", tags=["Status"])
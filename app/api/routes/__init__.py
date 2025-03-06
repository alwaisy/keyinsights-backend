# app/api/routes/__init__.py
from fastapi import APIRouter

from app.api.routes import transcript, insights, combined, status, websocket, limits

api_router = APIRouter()
api_router.include_router(transcript.router, prefix="/transcript", tags=["Transcript"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(combined.router, prefix="/combined", tags=["Combined"])
api_router.include_router(status.router, prefix="/status", tags=["Status"])
api_router.include_router(limits.router, prefix="/limits", tags=["Limits"])
api_router.include_router(websocket.router, tags=["WebSocket"])

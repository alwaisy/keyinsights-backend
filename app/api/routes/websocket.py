# app/api/routes/websocket.py
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, request_id: str):
        await websocket.accept()
        if request_id not in self.active_connections:
            self.active_connections[request_id] = []
        self.active_connections[request_id].append(websocket)

    def disconnect(self, websocket: WebSocket, request_id: str):
        if request_id in self.active_connections:
            if websocket in self.active_connections[request_id]:
                self.active_connections[request_id].remove(websocket)
            if not self.active_connections[request_id]:
                del self.active_connections[request_id]

    async def send_update(self, request_id: str, data: dict):
        if request_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[request_id]:
                try:
                    await connection.send_json(data)
                except Exception:
                    disconnected.append(connection)

            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection, request_id)


manager = ConnectionManager()


@router.websocket("/ws/{request_id}")
async def websocket_endpoint(websocket: WebSocket, request_id: str):
    # Accept the connection
    await websocket.accept()
    print(f"WebSocket connection accepted for request_id: {request_id}")

    try:
        # Get initial status directly, avoiding any new event loop creation
        from app.services.redis_service import RedisService
        redis = RedisService()

        # Get status synchronously to avoid event loop issues
        status = await redis.get_status(request_id)
        print(f"Initial status fetched for {request_id}: {status.get('status', 'unknown')}")

        # Send initial status
        if status:
            await websocket.send_json(status)
            print(f"Initial status sent for {request_id}")
        else:
            await websocket.send_json({"status": "not_found", "message": "Request not found"})

        # Keep the connection open and listen for pings
        while True:
            data = await websocket.receive_text()
            print(f"Received WebSocket message: {data}")

            if data == "ping":
                await websocket.send_text("pong")
                print("Sent pong response")

                # Optionally refresh and send status on ping
                try:
                    current_status = await redis.get_status(request_id)
                    if current_status:
                        await websocket.send_json(current_status)
                        print(f"Refreshed status sent for {request_id}")
                except Exception as status_err:
                    print(f"Error refreshing status: {status_err}")

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for {request_id}")
    except Exception as e:
        print(f"WebSocket error for {request_id}: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(traceback.format_exc())

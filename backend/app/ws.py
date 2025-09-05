"""
WebSocket manager for real-time advisory streaming.

Handles WebSocket connections and real-time advisory delivery.
"""

import json
import uuid
from typing import Dict, List, Set

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        # Store connections by farmer_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, farmer_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        
        if farmer_id not in self.active_connections:
            self.active_connections[farmer_id] = set()
        
        self.active_connections[farmer_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, farmer_id: str):
        """Remove WebSocket connection."""
        if farmer_id in self.active_connections:
            self.active_connections[farmer_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[farmer_id]:
                del self.active_connections[farmer_id]
    
    async def send_personal_message(self, message: str, farmer_id: str):
        """Send message to specific farmer."""
        if farmer_id in self.active_connections:
            connections = self.active_connections[farmer_id].copy()
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    # Remove failed connections
                    self.active_connections[farmer_id].discard(connection)
    
    async def send_advisory(self, advisory_data: dict, farmer_id: str):
        """Send advisory to farmer."""
        message = json.dumps({
            "type": "advisory",
            "data": advisory_data,
            "timestamp": advisory_data.get("timestamp"),
        })
        await self.send_personal_message(message, farmer_id)
    
    async def send_reminder(self, reminder_data: dict, farmer_id: str):
        """Send reminder to farmer."""
        message = json.dumps({
            "type": "reminder",
            "data": reminder_data,
            "timestamp": reminder_data.get("due_ts"),
        })
        await self.send_personal_message(message, farmer_id)
    
    async def send_notification(self, notification_data: dict, farmer_id: str):
        """Send notification to farmer."""
        message = json.dumps({
            "type": "notification",
            "data": notification_data,
            "timestamp": notification_data.get("created_at"),
        })
        await self.send_personal_message(message, farmer_id)
    
    def get_connection_count(self, farmer_id: str) -> int:
        """Get number of active connections for farmer."""
        return len(self.active_connections.get(farmer_id, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()

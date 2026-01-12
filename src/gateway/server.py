"""
FastAPI WebSocket server for Gateway signaling.

Responsibilities:
- Accept WebSocket connections from agents
- Manage agent presence/registry
- Route signaling messages (OFFER, ANSWER, ICE_CANDIDATE)
- Handle disconnections and timeouts

Does NOT route data plane messages - those go P2P.
"""

from typing import Dict, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import asyncio
import logging
import json
from datetime import datetime, timedelta

from aiconexus.protocol.models import Message, MessageType
from aiconexus.protocol.errors import ProtocolError, ConnectionError
from aiconexus.protocol.serialization import MessageSerializer
from .registry import AgentRegistry, RegistryEntry

logger = logging.getLogger(__name__)


class GatewayServer:
    """
    WebSocket Gateway server for signaling.
    
    Handles:
    - REGISTER: Agent announces itself
    - UNREGISTER: Agent goes offline
    - OFFER/ANSWER/ICE_CANDIDATE: Route to target agent
    
    Usage:
        from gateway import GatewayServer
        
        server = GatewayServer(agent_timeout=300)
        
        # Use with uvicorn
        # uvicorn gateway:app --host 0.0.0.0 --port 8000
    """
    
    def __init__(self, agent_timeout: int = 300, cleanup_interval: int = 60):
        """
        Initialize Gateway server.
        
        Args:
            agent_timeout: Seconds before agent is considered offline
            cleanup_interval: Seconds between expired agent cleanups
        """
        self.app = FastAPI(
            title="AIConexus Gateway",
            description="WebSocket signaling server for agent communication",
            version="0.1.0"
        )
        self.registry = AgentRegistry(timeout_seconds=agent_timeout)
        self._agents_by_ws: Dict[WebSocket, str] = {}  # Map WebSocket to agent_did
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = cleanup_interval
        
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Configure FastAPI routes."""
        
        @self.app.on_event("startup")
        async def startup():
            """Start cleanup task on server startup."""
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_agents())
            logger.info("Gateway startup - cleanup task started")
        
        @self.app.on_event("shutdown")
        async def shutdown():
            """Stop cleanup task on server shutdown."""
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            logger.info("Gateway shutdown")
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            agent_count = len(self.registry)
            return {
                "status": "healthy",
                "connected_agents": agent_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @self.app.get("/agents")
        async def list_agents():
            """List all connected agents."""
            agents = await self.registry.list_agents()
            return {
                "agents": [
                    {
                        "did": agent.agent_did,
                        "connected_at": agent.connected_at.isoformat(),
                        "last_activity": agent.last_activity.isoformat(),
                    }
                    for agent in agents
                ],
                "count": len(agents)
            }
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for agents."""
            await self._handle_connection(websocket)
    
    async def _cleanup_expired_agents(self) -> None:
        """Periodically clean up expired agents."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                removed = await self.registry.cleanup_expired()
                if removed:
                    logger.info(f"Cleaned up {removed} expired agents")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in cleanup task: {e}")
    
    async def _handle_connection(self, websocket: WebSocket) -> None:
        """
        Handle WebSocket connection from an agent.
        
        Lifecycle:
        1. Accept connection
        2. Wait for REGISTER message
        3. Route messages until disconnect
        4. Clean up agent
        """
        agent_did = None
        try:
            # Accept connection
            await websocket.accept(subprotocol="ioap.v1")
            logger.debug(f"WebSocket connected from {websocket.client}")
            
            # Wait for REGISTER message
            register_data = await websocket.receive_text()
            register_msg = json.loads(register_data)
            
            # Validate REGISTER message
            msg_obj = Message(**register_msg)
            if msg_obj.type != MessageType.REGISTER:
                error_msg = {
                    "type": "ERROR",
                    "from": "did:key:gateway",
                    "to": msg_obj.from_did,
                    "payload": {
                        "code": "INVALID_MESSAGE",
                        "message": "First message must be REGISTER"
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "signature": "",
                    "id": msg_obj.id,
                }
                await websocket.send_text(json.dumps(error_msg))
                await websocket.close()
                return
            
            agent_did = msg_obj.from_did
            public_key = msg_obj.payload.get("public_key")
            
            # Register agent in registry
            entry = RegistryEntry(
                agent_did=agent_did,
                public_key=public_key,
                connected_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                ip_address=websocket.client.host if websocket.client else "unknown"
            )
            await self.registry.register(agent_did, entry)
            self._agents_by_ws[websocket] = agent_did
            
            logger.info(f"Agent registered: {agent_did}")
            
            # Route messages until disconnect
            while True:
                message_data = await websocket.receive_text()
                await self._route_message(websocket, agent_did, message_data)
        
        except WebSocketDisconnect:
            logger.debug(f"WebSocket disconnected: {agent_did}")
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON received: {e}")
        except Exception as e:
            logger.exception(f"Error in WebSocket handler: {e}")
        finally:
            # Clean up
            if websocket in self._agents_by_ws:
                del self._agents_by_ws[websocket]
            if agent_did:
                await self.registry.unregister(agent_did)
                logger.info(f"Agent unregistered: {agent_did}")
    
    async def _route_message(
        self,
        sender_ws: WebSocket,
        sender_did: str,
        message_data: str
    ) -> None:
        """
        Route a message to its target agent.
        
        Args:
            sender_ws: WebSocket of sending agent
            sender_did: DID of sending agent
            message_data: JSON message string
        """
        try:
            message_dict = json.loads(message_data)
            msg = Message(**message_dict)
            
            # Update sender's activity
            await self.registry.touch(sender_did)
            
            # Handle different message types
            if msg.type == MessageType.OFFER:
                # Route OFFER to target agent
                await self._send_to_agent(msg.to_did, message_data)
            
            elif msg.type == MessageType.ANSWER:
                # Route ANSWER to target agent
                await self._send_to_agent(msg.to_did, message_data)
            
            elif msg.type == MessageType.ICE_CANDIDATE:
                # Route ICE candidate to target agent
                await self._send_to_agent(msg.to_did, message_data)
            
            elif msg.type == MessageType.PING:
                # Send PONG back
                pong_msg = {
                    "id": msg.id,
                    "type": "PONG",
                    "from": "did:key:gateway",
                    "to": sender_did,
                    "payload": msg.payload if hasattr(msg, 'payload') else {},
                    "timestamp": datetime.utcnow().isoformat(),
                    "signature": "",
                    "correlation_id": msg.id,
                }
                await sender_ws.send_text(json.dumps(pong_msg))
            
            else:
                logger.debug(f"Ignoring message type: {msg.type}")
        
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in routed message: {e}")
        except Exception as e:
            logger.warning(f"Error routing message: {e}")
    
    async def _send_to_agent(self, target_did: str, message_data: str) -> None:
        """
        Send a message to a specific agent.
        
        Args:
            target_did: Target agent's DID
            message_data: JSON message to send
        """
        # Look up target agent's WebSocket
        entry = await self.registry.get(target_did)
        if not entry:
            logger.warning(f"Target agent not found: {target_did}")
            return
        
        # Find WebSocket for this agent
        for ws, did in self._agents_by_ws.items():
            if did == target_did:
                try:
                    await ws.send_text(message_data)
                    await self.registry.touch(target_did)
                    logger.debug(f"Message routed to {target_did}")
                except Exception as e:
                    logger.warning(f"Failed to send to {target_did}: {e}")
                return


def create_app(
    agent_timeout: int = 300,
    cleanup_interval: int = 60
) -> FastAPI:
    """
    Create Gateway FastAPI application.
    
    Args:
        agent_timeout: Seconds before agent is considered offline
        cleanup_interval: Seconds between cleanup runs
    
    Returns:
        FastAPI application ready to run with uvicorn
    
    Usage:
        app = create_app()
        # uvicorn <module>:app --host 0.0.0.0 --port 8000
    """
    server = GatewayServer(
        agent_timeout=agent_timeout,
        cleanup_interval=cleanup_interval
    )
    return server.app

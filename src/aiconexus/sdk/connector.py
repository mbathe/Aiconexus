"""
Agent Connector
Handles P2P communication between agents with resilience
"""

from typing import List, Optional, Dict, Any
import asyncio
import uuid
import logging
from datetime import datetime
from abc import ABC, abstractmethod

from .types import (
    ConnectionInfo,
    Message,
    MessageResponse,
    AgentInfo
)
from .registry import AgentRegistry

logger = logging.getLogger(__name__)


class TransportProtocol(ABC):
    """Abstract transport protocol"""
    
    @abstractmethod
    async def send(self, connection_info: ConnectionInfo, message: Message) -> Dict[str, Any]:
        """Send a message"""
        pass


class HTTPTransport(TransportProtocol):
    """HTTP transport"""
    
    async def send(self, connection_info: ConnectionInfo, message: Message) -> Dict[str, Any]:
        """Send message over HTTP"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{connection_info.url}/message",
                    json={
                        "request_id": message.request_id,
                        "source_agent": message.source_agent,
                        "target_agent": message.target_agent,
                        "payload": message.payload,
                        "timestamp": message.timestamp.isoformat()
                    },
                    timeout=aiohttp.ClientTimeout(total=message.timeout_ms / 1000),
                    headers={
                        "Authorization": f"Bearer {connection_info.auth_token}" 
                        if connection_info.auth_token else ""
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
        
        except asyncio.TimeoutError:
            raise TimeoutError(f"HTTP request timeout after {message.timeout_ms}ms")
        except Exception as e:
            raise Exception(f"HTTP transport error: {str(e)}")


class WebSocketTransport(TransportProtocol):
    """WebSocket transport for real-time communication"""
    
    async def send(self, connection_info: ConnectionInfo, message: Message) -> Dict[str, Any]:
        """Send message over WebSocket"""
        try:
            import websockets
            
            uri = f"ws://{connection_info.host}:{connection_info.port}/ws"
            
            async with websockets.connect(
                uri,
                ping_interval=None,
                close_timeout=message.timeout_ms / 1000
            ) as websocket:
                # Send message
                await websocket.send(message.to_json())
                
                # Receive response with timeout
                response_text = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=message.timeout_ms / 1000
                )
                
                import json
                return json.loads(response_text)
        
        except asyncio.TimeoutError:
            raise TimeoutError(f"WebSocket request timeout after {message.timeout_ms}ms")
        except Exception as e:
            raise Exception(f"WebSocket transport error: {str(e)}")


class AgentConnector:
    """
    Main connector for agent communication
    Handles retry, timeout, error handling, and connection pooling
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        default_timeout_ms: int = 30000,
        max_retries: int = 3,
        enable_pooling: bool = True
    ):
        self.registry = registry
        self.default_timeout_ms = default_timeout_ms
        self.max_retries = max_retries
        self.enable_pooling = enable_pooling
        
        # Transport protocols
        self.transports = {
            "http": HTTPTransport(),
            "websocket": WebSocketTransport(),
        }
        
        # Connection pool
        self._connection_pool: Dict[str, Any] = {}
    
    async def send_message(
        self,
        to_agent_id: str,
        message: Dict[str, Any],
        source_agent_id: str,
        timeout_ms: Optional[int] = None,
        auto_validate: bool = True
    ) -> MessageResponse:
        """
        Send a message to another agent
        
        Returns: MessageResponse with result or error
        """
        
        timeout_ms = timeout_ms or self.default_timeout_ms
        request_id = str(uuid.uuid4())
        
        try:
            # Step 1: Get agent info
            target_agent = await self.registry.get_agent(to_agent_id)
            if not target_agent:
                return MessageResponse(
                    agent_id=to_agent_id,
                    request_id=request_id,
                    status="error",
                    error=f"Agent not found: {to_agent_id}"
                )
            
            # Step 2: Create message
            msg = Message(
                request_id=request_id,
                source_agent=source_agent_id,
                target_agent=to_agent_id,
                payload=message,
                timeout_ms=timeout_ms
            )
            
            # Step 3: Send with retries
            response = await self._send_with_retries(
                target_agent.connection_info,
                msg,
                self.max_retries
            )
            
            logger.info(
                f"{source_agent_id} → {to_agent_id}: SUCCESS "
                f"({response.get('_execution_time', 0):.0f}ms)"
            )
            
            return MessageResponse(
                agent_id=to_agent_id,
                request_id=request_id,
                response=response,
                status="success",
                execution_time_ms=response.get("_execution_time", 0)
            )
        
        except TimeoutError:
            logger.warning(f"{source_agent_id} → {to_agent_id}: ⏱️ TIMEOUT")
            return MessageResponse(
                agent_id=to_agent_id,
                request_id=request_id,
                status="timeout",
                error=f"Agent did not respond within {timeout_ms}ms"
            )
        
        except Exception as e:
            logger.error(f"{source_agent_id} → {to_agent_id}:  ERROR: {str(e)}")
            return MessageResponse(
                agent_id=to_agent_id,
                request_id=request_id,
                status="error",
                error=str(e)
            )
    
    async def send_messages_parallel(
        self,
        messages: List[Dict[str, Any]],
        agent_ids: List[str],
        source_agent_id: str,
        timeout_ms: Optional[int] = None
    ) -> List[MessageResponse]:
        """
        Send multiple messages in parallel
        """
        
        if len(messages) != len(agent_ids):
            raise ValueError("messages and agent_ids must have same length")
        
        # Create tasks for all messages
        tasks = [
            self.send_message(
                agent_id,
                message,
                source_agent_id,
                timeout_ms
            )
            for agent_id, message in zip(agent_ids, messages)
        ]
        
        # Execute all in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=False)
        
        return responses
    
    async def _send_with_retries(
        self,
        connection_info: ConnectionInfo,
        message: Message,
        max_retries: int
    ) -> Dict[str, Any]:
        """
        Send a message with exponential backoff retry logic
        """
        
        protocol = connection_info.protocol.lower()
        transport = self.transports.get(protocol)
        
        if not transport:
            raise ValueError(f"Unsupported protocol: {protocol}")
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Send the message
                start_time = datetime.utcnow()
                response = await transport.send(connection_info, message)
                elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                response["_execution_time"] = elapsed
                return response
            
            except TimeoutError as e:
                last_error = e
                if attempt == max_retries - 1:
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{max_retries}, "
                    f"retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(
                    f"Error on attempt {attempt + 1}/{max_retries}: {str(e)}, "
                    f"retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
        
        raise last_error or Exception("Max retries exceeded")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "pool_size": len(self._connection_pool),
            "pooling_enabled": self.enable_pooling
        }

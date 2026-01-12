#!/usr/bin/env python3
"""
Simple Ollama Agent Example

This example demonstrates how to create an agent that:
1. Uses Ollama with a lightweight local model (e.g., mistral or neural-chat)
2. Connects to the AIConexus gateway
3. Registers itself and communicates with other agents

Prerequisites:
    1. Install Ollama from https://ollama.ai
    2. Pull a lightweight model: ollama pull mistral (or neural-chat, phi, etc.)
    3. Start Ollama: ollama serve (runs on localhost:11434)
    4. Start the AIConexus gateway: poetry run python gateway_listen.py
"""

import asyncio
import logging
from typing import Optional
import json
import requests

from aiconexus.core.agent import Agent
from aiconexus.core.types import Message
from aiconexus.connector.websocket import WebSocketConnector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaAgent(Agent):
    """An agent powered by Ollama that can connect to the AIConexus gateway"""

    def __init__(
        self,
        name: str = "ollama-agent",
        ollama_model: str = "mistral",
        ollama_base_url: str = "http://localhost:11434",
        gateway_url: str = "ws://127.0.0.1:8000/ws",
        **kwargs
    ):
        """
        Initialize the Ollama agent

        Args:
            name: Agent name
            ollama_model: Ollama model to use (mistral, neural-chat, phi, etc.)
            ollama_base_url: Ollama server URL
            gateway_url: Gateway WebSocket URL
        """
        super().__init__(name=name, **kwargs)

        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.gateway_url = gateway_url

        # Initialize connector
        self.connector = WebSocketConnector(
            agent_id=self.agent_id,
            gateway_url=self.gateway_url
        )

        logger.info(f"Initialized OllamaAgent: {name}")
        logger.info(f"  Model: {ollama_model}")
        logger.info(f"  Ollama: {ollama_base_url}")
        logger.info(f"  Gateway: {gateway_url}")

    async def initialize(self) -> None:
        """Initialize the agent and connect to gateway"""
        logger.info(f"Initializing agent {self.name}...")

        # Check Ollama connectivity
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            response.raise_for_status()
            models = response.json()
            logger.info(f"Ollama is running with models: {models}")
        except Exception as e:
            logger.error(f"Cannot connect to Ollama at {self.ollama_base_url}")
            logger.error(f"Please start Ollama with: ollama serve")
            logger.error(f"And pull a model with: ollama pull {self.ollama_model}")
            raise

        # Register capabilities
        self._register_capabilities()

        # Connect to gateway
        try:
            await self.connector.connect()
            logger.info("Connected to AIConexus gateway")

            # Register with gateway
            await self.connector.register(
                agent_info={
                    "name": self.name,
                    "description": f"AI Agent powered by Ollama ({self.ollama_model})",
                    "capabilities": ["reasoning", "qa", "analysis"],
                    "llm_model": self.ollama_model,
                }
            )
            logger.info("Registered with gateway")

        except Exception as e:
            logger.error(f"Cannot connect to gateway at {self.gateway_url}")
            logger.error(f"Please start the gateway with: poetry run python gateway_listen.py")
            raise

    def _register_capabilities(self) -> None:
        """Register agent capabilities"""
        self.register_capability(
            capability_id="reasoning",
            name="Reasoning",
            description="Perform reasoning and analysis on complex topics",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The question or prompt to reason about"
                    }
                },
                "required": ["prompt"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "reasoning": {"type": "string"}
                }
            },
            sla={
                "latency_ms": 5000,
                "availability_percent": 99.0,
                "timeout_ms": 30000
            },
            pricing={
                "model_type": "per_call",
                "base_cost": "0.001",
                "unit": "call",
                "currency": "AIC"
            }
        )

        self.register_capability(
            capability_id="qa",
            name="Question Answering",
            description="Answer questions on various topics",
            input_schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to answer"
                    }
                },
                "required": ["question"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "confidence": {"type": "number"}
                }
            },
            sla={
                "latency_ms": 3000,
                "availability_percent": 99.5,
                "timeout_ms": 15000
            },
            pricing={
                "model_type": "per_call",
                "base_cost": "0.0005",
                "unit": "call",
                "currency": "AIC"
            }
        )

    async def shutdown(self) -> None:
        """Shutdown the agent"""
        logger.info(f"Shutting down agent {self.name}...")
        if self.connector:
            await self.connector.disconnect()
        logger.info("Agent shutdown complete")

    async def execute_capability(self, capability_id: str, input_params: dict) -> dict:
        """Execute a capability using Ollama"""

        if capability_id == "reasoning":
            return await self._handle_reasoning(input_params)
        elif capability_id == "qa":
            return await self._handle_qa(input_params)
        else:
            logger.warning(f"Unknown capability: {capability_id}")
            return {"error": f"Unknown capability: {capability_id}"}

    async def _handle_reasoning(self, input_params: dict) -> dict:
        """Handle reasoning capability"""
        prompt = input_params.get("prompt", "")

        if not prompt:
            return {"error": "Prompt is required"}

        try:
            logger.info(f"Reasoning about: {prompt}")

            response = await asyncio.to_thread(
                self._call_ollama,
                prompt,
                temperature=0.7
            )

            return {
                "response": response,
                "reasoning": f"Processed with {self.ollama_model}",
                "success": True
            }

        except Exception as e:
            logger.error(f"Error during reasoning: {e}")
            return {"error": str(e), "success": False}

    async def _handle_qa(self, input_params: dict) -> dict:
        """Handle question answering capability"""
        question = input_params.get("question", "")

        if not question:
            return {"error": "Question is required"}

        try:
            logger.info(f"Answering question: {question}")

            # Format prompt for QA
            qa_prompt = f"Please answer this question concisely: {question}"

            response = await asyncio.to_thread(
                self._call_ollama,
                qa_prompt,
                temperature=0.3
            )

            return {
                "answer": response,
                "confidence": 0.85,
                "model": self.ollama_model,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error during QA: {e}")
            return {"error": str(e), "success": False}

    def _call_ollama(self, prompt: str, temperature: float = 0.7) -> str:
        """Call Ollama API synchronously"""
        try:
            url = f"{self.ollama_base_url}/api/generate"

            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            }

            logger.debug(f"Calling Ollama: {url}")

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "No response from model")

        except requests.exceptions.Timeout:
            raise TimeoutError(f"Ollama request timed out after 30 seconds")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.ollama_base_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def send_message(self, recipient_id: str, content: str) -> bool:
        """Send a message to another agent via gateway"""
        try:
            message = Message(
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                content=content,
                message_type="agent_message"
            )
            await self.connector.send_message(message)
            logger.info(f"Sent message to {recipient_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def receive_messages(self) -> Optional[Message]:
        """Receive messages from other agents (non-blocking)"""
        try:
            message = await self.connector.receive_message()
            if message:
                logger.info(f"Received message from {message.sender_id}: {message.content}")
            return message
        except Exception as e:
            logger.debug(f"No messages available: {e}")
            return None


async def main():
    """Main example: create and run an Ollama agent"""

    print("\n" + "="*70)
    print("AIConexus - Ollama Agent Example")
    print("="*70)

    # Create the agent
    agent = OllamaAgent(
        name="ollama-qa-agent",
        ollama_model="phi",  # Lightweight model (3B, 2GB RAM)
        ollama_base_url="http://localhost:11434",
        gateway_url="ws://127.0.0.1:8000/ws"
    )

    try:
        # Initialize (connect to gateway and Ollama)
        await agent.initialize()

        print("\n" + "-"*70)
        print("Agent is ready. Testing capabilities...")
        print("-"*70)

        # Test reasoning capability
        print("\n1. Testing Reasoning Capability:")
        reasoning_result = await agent.execute_capability(
            "reasoning",
            {"prompt": "What are the main benefits of machine learning?"}
        )
        print(f"Result: {reasoning_result['response'][:200]}...")

        # Test QA capability
        print("\n2. Testing QA Capability:")
        qa_result = await agent.execute_capability(
            "qa",
            {"question": "What is Python?"}
        )
        print(f"Answer: {qa_result['answer'][:200]}...")

        # Keep agent running for 30 seconds to allow gateway communication
        print("\n3. Agent is running and connected to gateway for 30 seconds...")
        print("   Other agents can now discover and communicate with this agent!")

        await asyncio.sleep(30)

    except ConnectionError as e:
        print(f"\nError: {e}")
        print("\nSetup Instructions:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Pull a model: ollama pull mistral")
        print("4. Start gateway: poetry run python gateway_listen.py")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

    finally:
        await agent.shutdown()
        print("\n" + "="*70)
        print("Example completed")
        print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

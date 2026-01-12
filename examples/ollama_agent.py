#!/usr/bin/env python3
"""
Real Ollama Agent using AIConexus SDK

This agent:
1. Extends the Agent base class from the SDK
2. Uses Ollama for LLM inference
3. Connects to the AIConexus gateway
4. Registers capabilities
5. Can be discovered and communicated with by other agents

Usage:
    Terminal 1: ./run_gateway.sh
    Terminal 2: PYTHONPATH=src python examples/ollama_agent.py
"""

import asyncio
import logging
from typing import Optional, Any, Dict
from uuid import uuid4
import requests

from aiconexus.core.agent import Agent, Capability

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OllamaAgent(Agent):
    """An AI agent powered by Ollama local LLM"""

    def __init__(
        self,
        name: str = "ollama-agent",
        ollama_model: str = "phi",
        ollama_base_url: str = "http://localhost:11434",
        **kwargs
    ):
        """Initialize the Ollama agent"""
        super().__init__(name=name, **kwargs)
        
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        
        logger.info(f"Created OllamaAgent: {name}")
        logger.info(f"  Agent ID: {self.agent_id}")
        logger.info(f"  Model: {ollama_model}")
        logger.info(f"  Ollama URL: {ollama_base_url}")

    async def initialize(self) -> None:
        """Initialize the agent"""
        logger.info(f"Initializing agent {self.name}...")
        
        # Check Ollama is available
        try:
            response = requests.get(
                f"{self.ollama_base_url}/api/tags",
                timeout=2
            )
            models = response.json().get("models", [])
            logger.info(f"Ollama is available with {len(models)} models")
            
            # Check if our model is available
            model_names = [m.get("name", "").split(":")[0] for m in models]
            if self.ollama_model.split(":")[0] not in model_names:
                logger.warning(
                    f"Model {self.ollama_model} not found. "
                    f"Available: {model_names}"
                )
        except Exception as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            logger.error("Start Ollama with: ollama serve")
            raise
        
        # Register capabilities
        self.register_capability(
            capability_id="reasoning",
            name="Reasoning",
            description="Perform reasoning and analysis using Ollama",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt for reasoning"
                    }
                },
                "required": ["prompt"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "model": {"type": "string"}
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
        
        logger.info("Agent initialized with capabilities")

    async def shutdown(self) -> None:
        """Shutdown the agent"""
        logger.info(f"Shutting down agent {self.name}")

    async def execute_capability(
        self,
        capability_id: str,
        input_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a capability"""
        
        if capability_id == "reasoning":
            prompt = input_params.get("prompt", "")
            if not prompt:
                return {"error": "Prompt is required"}
            
            try:
                logger.info(f"Reasoning about: {prompt[:100]}...")
                
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30
                )
                
                result = response.json()
                answer = result.get("response", "No response")
                
                return {
                    "response": answer,
                    "model": self.ollama_model,
                    "success": True
                }
            
            except Exception as e:
                logger.error(f"Error executing reasoning: {e}")
                return {"error": str(e), "success": False}
        
        else:
            return {"error": f"Unknown capability: {capability_id}"}


async def main():
    """Run the agent"""
    
    print("\n" + "="*70)
    print("AIConexus - Ollama Agent with SDK".center(70))
    print("="*70 + "\n")
    
    # Create agent
    agent = OllamaAgent(
        name="ollama-qa-agent",
        ollama_model="phi"
    )
    
    try:
        # Initialize
        await agent.initialize()
        
        print("\n" + "-"*70)
        print("Agent ready with capabilities:")
        print("-"*70)
        for cap_id, cap in agent.capabilities.items():
            print(f"  - {cap.name} ({cap_id})")
            print(f"    {cap.description}")
        
        # Test capability
        print("\n" + "-"*70)
        print("Testing capability execution...")
        print("-"*70 + "\n")
        
        result = await agent.execute_capability(
            "reasoning",
            {"prompt": "What is machine learning? Answer in 2 sentences."}
        )
        
        if result.get("success"):
            print(f"Response:\n{result.get('response')}\n")
        else:
            print(f"Error: {result.get('error')}\n")
        
        # Keep running for 30 seconds to allow gateway discovery
        print("-"*70)
        print("Agent running for 30 seconds (allow gateway to discover)...")
        print("-"*70)
        print("To connect with gateway:")
        print("  Terminal 1: ./run_gateway.sh")
        print("  Terminal 2: PYTHONPATH=src python examples/ollama_agent.py")
        print("-"*70 + "\n")
        
        await asyncio.sleep(30)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    
    finally:
        await agent.shutdown()
        print("\n" + "="*70)
        print("Agent stopped".center(70))
        print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

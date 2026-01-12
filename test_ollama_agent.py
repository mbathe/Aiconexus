#!/usr/bin/env python3
"""
Simple Ollama Agent Test

Tests connection to:
1. Ollama (local LLM)
2. AIConexus Gateway (agent network)
"""

import asyncio
import logging
import requests
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_ollama(
    model: str = "phi",
    ollama_url: str = "http://localhost:11434"
) -> bool:
    """Test Ollama connectivity and inference"""
    
    print("\n" + "="*70)
    print("Testing Ollama Connection".center(70))
    print("="*70 + "\n")
    
    try:
        # Test 1: Check Ollama is running
        logger.info("1. Checking Ollama is running...")
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        models = response.json()
        logger.info(f"   Ollama is running!")
        logger.info(f"   Available models: {len(models.get('models', []))}")
        
        # Test 2: Try inference
        logger.info(f"2. Testing inference with {model}...")
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": "What is machine learning? Answer briefly.",
                "stream": False
            },
            timeout=60
        )
        
        result = response.json()
        answer = result.get("response", "No response")
        
        logger.info(f"   Model response:")
        logger.info(f"   {answer[:150]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        return False


async def test_gateway(
    gateway_url: str = "ws://127.0.0.1:8000/ws"
) -> bool:
    """Test Gateway connectivity"""
    
    print("\n" + "="*70)
    print("Testing Gateway Connection".center(70))
    print("="*70 + "\n")
    
    try:
        import websockets
        
        logger.info(f"Connecting to gateway: {gateway_url}")
        
        async with websockets.connect(gateway_url, ping_interval=None) as ws:
            logger.info("Connected!")
            
            # Send registration message
            message = {
                "type": "register",
                "agent_id": "test-ollama-agent",
                "name": "Ollama Test Agent",
                "capabilities": ["reasoning", "qa"]
            }
            
            await ws.send(json.dumps(message))
            logger.info("Registration message sent")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                logger.info(f"Received response: {response[:100]}...")
                return True
            except asyncio.TimeoutError:
                logger.warning("No response from gateway")
                return False
    
    except ImportError:
        logger.error("websockets library not installed")
        return False
    except Exception as e:
        logger.error(f"Failed: {e}")
        return False


async def main():
    """Run all tests"""
    
    print("\n" + "="*70)
    print("AIConexus + Ollama - Agent Gateway Test".center(70))
    print("="*70)
    
    results = {
        "ollama": await test_ollama(),
        "gateway": await test_gateway()
    }
    
    # Summary
    print("\n" + "="*70)
    print("Summary".center(70))
    print("="*70 + "\n")
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} Ollama connection........... [{status}]" if test_name == "ollama" else f"  {symbol} Gateway connection......... [{status}]")
    
    print()
    
    if results.get("ollama") and results.get("gateway"):
        print("  SUCCESS: Both connections working!")
        print()
        print("  Next: Run full agent test")
        print("    Terminal 1: ./run_gateway.sh")
        print("    Terminal 2: python examples/test_ollama_agent.py")
    else:
        if not results.get("ollama"):
            print("  ISSUE: Ollama not responding")
            print("  Fix: ollama serve")
        if not results.get("gateway"):
            print("  ISSUE: Gateway not responding")
            print("  Fix: ./run_gateway.sh")
    
    print("\n" + "="*70 + "\n")
    
    return all(results.values())


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

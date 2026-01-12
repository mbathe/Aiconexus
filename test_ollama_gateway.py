#!/usr/bin/env python3
"""
Minimal Ollama + AIConexus Gateway Test

This is the simplest possible example to test:
1. Ollama connectivity
2. Gateway connectivity  
3. Agent capability execution
"""

import asyncio
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_ollama(ollama_url: str = "http://localhost:11434"):
    """Test Ollama connectivity"""
    print("\n1. Testing Ollama Connection")
    print("-" * 50)
    
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        models = response.json()
        logger.info(f"Ollama is running!")
        logger.info(f"Available models: {len(models.get('models', []))}")
        
        if models.get("models"):
            for model in models["models"][:3]:
                logger.info(f"  - {model['name']}")
        return True
        
    except Exception as e:
        logger.error(f"Cannot connect to Ollama at {ollama_url}")
        logger.error("Start Ollama with: ollama serve")
        return False


async def test_ollama_inference(
    ollama_url: str = "http://localhost:11434",
    model: str = "phi"
):
    """Test Ollama inference"""
    print("\n2. Testing Ollama Inference")
    print("-" * 50)
    
    try:
        logger.info(f"Using model: {model}")
        logger.info("Sending request to Ollama...")
        
        prompt = "What is machine learning? Answer in one sentence."
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        result = response.json()
        answer = result.get("response", "No response")
        
        logger.info(f"Model response:")
        logger.info(f"  {answer}")
        return True
        
    except requests.exceptions.Timeout:
        logger.error("Request timed out. Model may be slow or not loaded.")
        return False
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return False


async def test_gateway(gateway_url: str = "ws://127.0.0.1:8000/ws"):
    """Test gateway connectivity"""
    print("\n3. Testing Gateway Connection")
    print("-" * 50)
    
    try:
        import websockets
        
        logger.info(f"Connecting to gateway: {gateway_url}")
        
        async with websockets.connect(gateway_url, ping_interval=None) as ws:
            logger.info("Connected to gateway!")
            logger.info(f"WebSocket connection established")
            
            # Send a simple hello message
            import json
            hello = json.dumps({
                "type": "hello",
                "agent_id": "test-agent",
                "name": "Test Agent"
            })
            
            await ws.send(hello)
            logger.info("Sent hello message to gateway")
            
            # Receive response
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            logger.info(f"Received: {response[:100]}...")
            
            return True
            
    except ImportError:
        logger.error("websockets library not installed")
        logger.error("Install with: pip install websockets")
        return False
    except asyncio.TimeoutError:
        logger.error("No response from gateway")
        logger.error("Start gateway with: poetry run python gateway_listen.py")
        return False
    except Exception as e:
        logger.error(f"Cannot connect to gateway at {gateway_url}")
        logger.error(f"Start gateway with: poetry run python gateway_listen.py")
        logger.error(f"Error: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("AIConexus + Ollama - Connectivity Test")
    print("=" * 70)
    
    results = {}
    
    # Test Ollama
    results["ollama_connection"] = await test_ollama()
    
    if results["ollama_connection"]:
        results["ollama_inference"] = await test_ollama_inference()
    else:
        logger.warning("Skipping inference test - Ollama not available")
        results["ollama_inference"] = False
    
    # Test Gateway
    results["gateway_connection"] = await test_gateway()
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:30} [{status}]")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed! You're ready to run the agent.")
        print("\nNext steps:")
        print("1. poetry run python examples/ollama_agent.py")
    else:
        print("\n✗ Some tests failed. Check the errors above.")
        print("\nMissing components:")
        if not results.get("ollama_connection"):
            print("  - Ollama: ollama serve")
        if not results.get("gateway_connection"):
            print("  - Gateway: poetry run python gateway_listen.py")
    
    print("\n" + "=" * 70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

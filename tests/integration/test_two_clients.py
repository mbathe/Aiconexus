import asyncio
import sys
from aiconexus.client.socket import GatewayClient
from aiconexus.protocol.security import DIDKey

async def run_client(client_id: int):
    """Run a single test client."""
    try:
        # Generate identity
        did_key = DIDKey.generate()
        print(f"[CLIENT {client_id}] DID: {did_key.public_key_base58[:20]}...")
        
        # Create client
        client = GatewayClient(
            gateway_url="ws://127.0.0.1:8000/ws",
            did_key=did_key
        )
        
        # Register message handler
        async def on_message(msg_dict):
            print(f"[CLIENT {client_id}] 📨 Message: {msg_dict.get('type', 'UNKNOWN')}")
        
        client.on_message(on_message)
        
        # Connect
        async with client:
            print(f"[CLIENT {client_id}] ✅ Connected to gateway")
            
            # Register
            await client.register(did_key.public_key_base58)
            print(f"[CLIENT {client_id}] ✅ Registered")
            
            # Stay connected for 10 seconds
            await asyncio.sleep(10)
            
        print(f"[CLIENT {client_id}] ✅ Disconnected gracefully")
        return True
        
    except Exception as e:
        print(f"[CLIENT {client_id}] ❌ Error: {e}")
        return False

async def main():
    """Run two clients concurrently."""
    print("\n" + "="*60)
    print("🚀 LAUNCHING TWO TEST CLIENTS")
    print("="*60 + "\n")
    
    print("[MAIN] Waiting 2 seconds for gateway to be ready...\n")
    await asyncio.sleep(2)
    
    # Run both clients concurrently
    results = await asyncio.gather(
        run_client(1),
        run_client(2),
        return_exceptions=True
    )
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    success = all(results)
    if success:
        print("✅ Both clients connected successfully!")
    else:
        print("❌ One or more clients failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

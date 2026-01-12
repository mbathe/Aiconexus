#!/usr/bin/env python
"""
Test avec deux clients qui s'échangent des messages via le gateway.
"""

import asyncio
import sys
from aiconexus.client.socket import GatewayClient
from aiconexus.protocol.security import DIDKey
from datetime import datetime

async def test_message_exchange():
    """Test message exchange between two clients."""
    print("\n" + "="*70)
    print("🔄 TWO-CLIENT MESSAGE EXCHANGE TEST")
    print("="*70 + "\n")
    
    # Generate identities
    did_key_1 = DIDKey.generate()
    did_key_2 = DIDKey.generate()
    
    client1_did = did_key_1.did  # Use the full DID, not public_key_base58
    client2_did = did_key_2.did
    
    print(f"[CLIENT 1] DID: {client1_did[:25]}...")
    print(f"[CLIENT 2] DID: {client2_did[:25]}...\n")
    
    # Create clients
    client1 = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key=did_key_1
    )
    client2 = GatewayClient(
        gateway_url="ws://127.0.0.1:8000/ws",
        did_key=did_key_2
    )
    
    # Message tracking
    messages_received_1 = []
    messages_received_2 = []
    
    async def on_message_1(msg_dict):
        messages_received_1.append(msg_dict)
        msg_type = msg_dict.get('type', 'UNKNOWN')
        print(f"[CLIENT 1] 📨 Received {msg_type}")
    
    async def on_message_2(msg_dict):
        messages_received_2.append(msg_dict)
        msg_type = msg_dict.get('type', 'UNKNOWN')
        print(f"[CLIENT 2] 📨 Received {msg_type}")
    
    client1.on_message(on_message_1)
    client2.on_message(on_message_2)
    
    try:
        # Connect both clients
        await client1.connect()
        await client2.connect()
        
        print("[CLIENT 1] ✅ Connected to gateway")
        print("[CLIENT 2] ✅ Connected to gateway\n")
        
        await client1.register(client1_did)
        await client2.register(client2_did)
        
        print("[CLIENT 1] ✅ Registered with gateway")
        print("[CLIENT 2] ✅ Registered with gateway\n")
        
        # Small delay to ensure registration
        await asyncio.sleep(0.5)
            
        # CLIENT 1 sends OFFER to CLIENT 2
        print("["+"─"*66+"]")
        print("[CLIENT 1] 📤 Sending OFFER to CLIENT 2...")
        print("["+"─"*66+"]")
        
        offer_msg_dict = {
            "id": "msg-1",
            "type": "OFFER",
            "from": client1_did,
            "to": client2_did,
            "payload": {"sdp": "v=0\no=- 0 0 IN IP4 127.0.0.1\n..."},
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "",
            "correlation_id": "test-1"
        }
        
        await client1.send(offer_msg_dict)
        
        # Wait for CLIENT 2 to receive OFFER
        await asyncio.sleep(1)
        
        if messages_received_2:
            print(f"[CLIENT 2] ✅ Received OFFER from CLIENT 1")
            print(f"   Payload keys: {list(messages_received_2[-1].get('payload', {}).keys())}")
        else:
            print(f"[CLIENT 2] ⚠️  Did not receive OFFER")
        
        print()
        
        # CLIENT 2 sends ANSWER back to CLIENT 1
        print("["+"─"*66+"]")
        print("[CLIENT 2] 📤 Sending ANSWER to CLIENT 1...")
        print("["+"─"*66+"]")
        
        answer_msg_dict = {
            "id": "msg-2",
            "type": "ANSWER",
            "from": client2_did,
            "to": client1_did,
            "payload": {"sdp": "v=0\no=- 0 0 IN IP4 127.0.0.1\n..."},
            "timestamp": datetime.utcnow().isoformat(),
            "signature": "",
            "correlation_id": "test-1"
        }
        
        await client2.send(answer_msg_dict)
        
        # Wait for CLIENT 1 to receive ANSWER
        await asyncio.sleep(1)
        
        if messages_received_1:
            print(f"[CLIENT 1] ✅ Received ANSWER from CLIENT 2")
            print(f"   Payload keys: {list(messages_received_1[-1].get('payload', {}).keys())}")
        else:
            print(f"[CLIENT 1] ⚠️  Did not receive ANSWER")
        
        # Cleanup
        await client1.disconnect()
        await client2.disconnect()
        
        # Summary
        print("\n" + "="*70)
        print("📊 EXCHANGE SUMMARY")
        print("="*70)
        print(f"[CLIENT 1] Received {len(messages_received_1)} message(s)")
        print(f"[CLIENT 2] Received {len(messages_received_2)} message(s)")
        
        if messages_received_1 and messages_received_2:
            print("\n✅ Two-way message exchange SUCCESSFUL!")
            return True
        else:
            print("\n⚠️  Message exchange incomplete")
            return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_message_exchange())
    sys.exit(0 if result else 1)

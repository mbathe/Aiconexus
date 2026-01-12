# IoAP Protocol Design Document v1.0

**Status**: VALIDATED FOR IMPLEMENTATION  
**Phase**: Phase 1 (MVP One-to-One)  
**Date**: January 12, 2026

---

## 1. Message Structure (Control Plane)

Standard format for WebSocket (Signaling) and DataChannel (Negotiation).

```json
{
  "id": "uuid_v4_unique_message_id",
  "correlation_id": "uuid_v4_optional_reply_to_id",
  "timestamp": "2026-01-12T10:00:00Z",
  "from": "did:key:z6MkClient...",
  "to": "did:key:z6MkExpert...",
  "type": "OFFER",
  "payload": {
    "sdp": "v=0..."
  },
  "version": "1.0",
  "signature": "base64_ed25519_signature"
}
```

**Notes**:
- `correlation_id`: Links EXEC_REQUEST with EXEC_RESPONSE for async handling
- `timestamp`: ISO 8601 UTC
- `signature`: Computed over canonical JSON (excludes this field)

---

## 2. Message Types (Enum)

| Type | Canal | Direction | Description |
|------|-------|-----------|-------------|
| REGISTER | Gateway | A → Gateway | Agent announces itself at startup |
| UNREGISTER | Gateway | A → Gateway | Agent graceful shutdown |
| OFFER | Gateway | A → B | WebRTC SDP Offer (initiate connection) |
| ANSWER | Gateway | B → A | WebRTC SDP Answer (accept) |
| ICE_CANDIDATE | Gateway | A ↔ B | Network candidates (IP:Port) for NAT traversal |
| INTENT | P2P | A → B | Semantic negotiation (Natural Language or Structured) |
| EXEC_REQUEST | P2P | A → B | Execution command with parameters |
| EXEC_RESPONSE | P2P | B → A | Execution result |
| ERROR | Any | A ↔ B | Protocol or application error |
| PING | Any | A ↔ B | Keep-alive request |
| PONG | Any | A ↔ B | Keep-alive response |

---

## 3. Call Flow (Sequence Diagram)

### Phase 1: Discovery & Signaling (WebSocket)

```
T0 (Register):
  Agent A → Gateway: {"type": "REGISTER", "did": "did:key:z6MkA..."}
  Agent B → Gateway: {"type": "REGISTER", "did": "did:key:z6MkB..."}
  Gateway: Records presence in registry

T1 (Offer):
  Agent A → Gateway: {"type": "OFFER", "to": "did:key:z6MkB...", "payload": {"sdp": "..."}}
  Gateway → Agent B: {"type": "OFFER", "from": "did:key:z6MkA...", "payload": {"sdp": "..."}}

T2 (Answer):
  Agent B → Gateway: {"type": "ANSWER", "to": "did:key:z6MkA...", "payload": {"sdp": "..."}}
  Gateway → Agent A: {"type": "ANSWER", "from": "did:key:z6MkB...", "payload": {"sdp": "..."}}

T2.5 (Trickle ICE - Parallel):
  Agent A discovers IP → Gateway: {"type": "ICE_CANDIDATE", "to": "z6MkB...", "payload": {"candidate": "..."}}
  Agent B discovers IP → Gateway: {"type": "ICE_CANDIDATE", "to": "z6MkA...", "payload": {"candidate": "..."}}
  Agents add candidates mutually
```

### Phase 2: P2P Established (DataChannel)

```
T3 (DataChannel Open):
  WebRTC connection established
  Gateway no longer used for message routing

T4 (Negotiation - Natural Language):
  Agent A → Agent B (P2P):
    {"type": "INTENT", "payload": {"query": "Extract non-compete clauses from this PDF"}}
  
  Agent B → Agent A (P2P):
    {"type": "INTENT", "payload": {"status": "understood", "required_input": "pdf_file", "cost": "0.50 EUR"}}

T5 (Execution):
  Agent A → Agent B (P2P):
    {"type": "EXEC_REQUEST", "correlation_id": "req_1", "payload": {"args": {"file_id": "temp_123"}}}
  
  Agent B executes processing...
  
  Agent B → Agent A (P2P):
    {"type": "EXEC_RESPONSE", "correlation_id": "req_1", "payload": {"result": "Clause found on page 3..."}}
```

---

## 4. Security & Signature

### Algorithm: Ed25519

**Key Properties**:
- Fast signing/verification
- Small key size (32 bytes)
- Cryptographically secure

### DID Format: did:key

**Structure**: `did:key:z6Mk<base58_public_key>`

**Advantages**:
- Decentralized (no blockchain or central authority needed)
- Offline-first verification
- Public key embedded in DID

### Signature Process (Sender)

1. Create message dictionary `msg`
2. Remove `signature` field if present
3. Generate Canonical JSON:
   ```python
   canonical = json.dumps(msg, separators=(',', ':'), sort_keys=True)
   ```
4. Sign canonical bytes with private key (Ed25519)
5. Encode signature in Base64 and add to message

### Verification Process (Receiver)

1. Extract `signature` and `from` (DID)
2. Extract public key from DID (did:key format contains it)
3. Reconstruct canonical JSON (without signature field)
4. Verify signature with public key
5. Raise error if verification fails

---

## 5. INTENT Payload Specification

Agents must support at least one mode for interoperability.

### Mode A: Natural Language (Human-like)

For LLM-driven agent-to-agent interactions.

```json
{
  "query": "I need to extract non-compete clauses from a contract",
  "context": "Priority: high, Language: French, Format: structured list"
}
```

### Mode B: Structured (Machine-like)

For high-performance or deterministic interactions.

```json
{
  "task": "extract_clauses",
  "params": {
    "file_id": "doc_123",
    "clause_types": ["non_compete", "confidentiality"],
    "output_format": "structured_list"
  }
}
```

---

## 6. Project Structure

```
src/aiconexus/protocol/
├── __init__.py
├── models.py              # Pydantic models for all message types
├── security.py            # DID generation, signing, verification
├── serialization.py       # Canonical JSON helpers
├── errors.py              # Protocol-specific exceptions
├── transport/
│   ├── __init__.py
│   ├── peer.py            # Wrapper around aiortc RTCPeerConnection
│   └── socket.py          # WebSocket client for signaling
├── gateway/
│   ├── __init__.py
│   ├── server.py          # FastAPI WebSocket server
│   └── registry.py        # In-memory presence table
└── agent.py               # High-level IoAPAgent class

tests/unit/protocol/
├── test_models.py
├── test_security.py
├── test_serialization.py
└── test_errors.py

tests/integration/protocol/
├── test_gateway.py
└── test_peer_connection.py
```

---

## 7. Implementation Roadmap

### Sprint 1: Foundation (Models & Security)
- `protocol/models.py`: Pydantic models for all message types
- `protocol/security.py`: DID and Ed25519 operations
- `protocol/serialization.py`: Canonical JSON utilities
- Unit tests

### Sprint 2: Transport Signaling
- `protocol/transport/socket.py`: WebSocket client
- `protocol/gateway/server.py`: Gateway FastAPI server
- `protocol/gateway/registry.py`: Presence management
- Integration tests

### Sprint 3: Transport P2P
- `protocol/transport/peer.py`: aiortc wrapper
- DataChannel management
- P2P tests

### Sprint 4: High-Level API
- `protocol/agent.py`: IoAPAgent class
- `connect()`, `execute_intent()` methods
- End-to-end tests

### Sprint 5: Documentation & Examples
- Example agents
- API documentation
- Deployment guide

---

## 8. Versioning

**Current Version**: 1.0  
**Compatibility**: Agents must handle `version` field in messages

Future protocol changes will increment version. Agents will implement version negotiation in Phase 2.

---

## 9. Error Codes (for ERROR message type)

| Code | Meaning |
|------|---------|
| INVALID_SIGNATURE | Signature verification failed |
| UNKNOWN_AGENT | Target agent not found in registry |
| CONNECTION_REFUSED | Target agent rejected connection |
| TIMEOUT | No response within timeout window |
| MALFORMED_MESSAGE | JSON parsing or schema validation failed |
| UNSUPPORTED_VERSION | Message version not supported |
| INTERNAL_ERROR | Server/agent internal error |

---

**End of Document**

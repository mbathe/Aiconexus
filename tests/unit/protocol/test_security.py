"""
Unit tests for protocol security (DID and signatures).
"""

import pytest
from aiconexus.protocol.security import DIDKey, MessageSigner


class TestDIDKey:
    """Test DID:key generation and operations."""
    
    def test_did_key_generate(self):
        """Test generating a new DID:key."""
        did_key = DIDKey.generate()
        assert did_key.did.startswith("did:key:z6Mk")
        assert len(did_key.private_key_bytes) == 32
        assert len(did_key.public_key_bytes) == 32
    
    def test_did_key_roundtrip(self):
        """Test generating and reconstructing a DID:key."""
        original = DIDKey.generate()
        original_did = original.did
        
        reconstructed = DIDKey.from_private_key_bytes(original.private_key_bytes)
        assert reconstructed.did == original_did
        assert reconstructed.public_key_bytes == original.public_key_bytes
    
    def test_did_key_sign_verify(self):
        """Test signing and verifying data."""
        did_key = DIDKey.generate()
        data = b"test message"
        
        signature = did_key.sign(data)
        assert len(signature) == 64
        assert did_key.verify(data, signature)
    
    def test_did_key_verify_fails_wrong_data(self):
        """Test that verification fails with modified data."""
        did_key = DIDKey.generate()
        data = b"test message"
        signature = did_key.sign(data)
        
        assert not did_key.verify(b"different message", signature)
    
    def test_did_key_verify_fails_wrong_signature(self):
        """Test that verification fails with invalid signature."""
        did_key = DIDKey.generate()
        data = b"test message"
        bad_signature = b"0" * 64
        
        assert not did_key.verify(data, bad_signature)
    
    def test_did_format(self):
        """Test DID format correctness."""
        did_key = DIDKey.generate()
        did = did_key.did
        
        assert did.startswith("did:key:z6Mk")
        parts = did.split(":")
        assert len(parts) == 3
        assert parts[0] == "did"
        assert parts[1] == "key"


class TestMessageSigner:
    """Test message signing and verification."""
    
    def test_canonical_json(self):
        """Test canonical JSON generation."""
        data = {"z": 3, "a": 1, "m": 2}
        canonical = MessageSigner.canonical_json(data)
        
        assert canonical == '{"a":1,"m":2,"z":3}'
        assert "z" in canonical
        assert " " not in canonical
    
    def test_canonical_json_deterministic(self):
        """Test that canonical JSON is deterministic."""
        data = {"x": 1, "y": 2}
        canonical1 = MessageSigner.canonical_json(data)
        canonical2 = MessageSigner.canonical_json(data)
        
        assert canonical1 == canonical2
    
    def test_sign_and_verify_message(self):
        """Test signing and verifying a message."""
        did_key = DIDKey.generate()
        message = {
            "id": "msg_123",
            "from": did_key.did,
            "to": "did:key:z6MkOther",
            "type": "INTENT",
            "payload": {"query": "test"}
        }
        
        signature = MessageSigner.sign_message(message, did_key)
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        verified = MessageSigner.verify_message(message, signature, did_key.did)
        assert verified is True
    
    def test_verify_fails_wrong_signature(self):
        """Test that verification fails with wrong signature."""
        did_key = DIDKey.generate()
        message = {"id": "msg_123", "data": "test"}
        
        verified = MessageSigner.verify_message(
            message,
            "invalid_signature_base64",
            did_key.did
        )
        assert verified is False
    
    def test_verify_fails_modified_message(self):
        """Test that verification fails if message is modified."""
        did_key = DIDKey.generate()
        message = {"id": "msg_123", "data": "test"}
        
        signature = MessageSigner.sign_message(message, did_key)
        
        message["data"] = "modified"
        verified = MessageSigner.verify_message(message, signature, did_key.did)
        assert verified is False
    
    def test_verify_fails_wrong_did(self):
        """Test that verification fails if sender DID is wrong."""
        did_key1 = DIDKey.generate()
        did_key2 = DIDKey.generate()
        
        message = {"id": "msg_123", "data": "test"}
        signature = MessageSigner.sign_message(message, did_key1)
        
        verified = MessageSigner.verify_message(message, signature, did_key2.did)
        assert verified is False
    
    def test_signature_is_base64(self):
        """Test that signature is properly Base64 encoded."""
        did_key = DIDKey.generate()
        message = {"id": "msg_123"}
        
        signature = MessageSigner.sign_message(message, did_key)
        
        try:
            import base64
            decoded = base64.b64decode(signature)
            assert len(decoded) == 64
        except Exception:
            pytest.fail("Signature is not valid Base64")
    
    def test_multiple_messages_different_signatures(self):
        """Test that different messages produce different signatures."""
        did_key = DIDKey.generate()
        msg1 = {"id": "msg_1"}
        msg2 = {"id": "msg_2"}
        
        sig1 = MessageSigner.sign_message(msg1, did_key)
        sig2 = MessageSigner.sign_message(msg2, did_key)
        
        assert sig1 != sig2
        assert MessageSigner.verify_message(msg1, sig1, did_key.did)
        assert MessageSigner.verify_message(msg2, sig2, did_key.did)
        assert not MessageSigner.verify_message(msg1, sig2, did_key.did)

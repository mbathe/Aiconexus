"""
Security operations for IoAP Protocol.

Handles DID generation, Ed25519 signing/verification, and key management.
"""

import json
import base64
from typing import Tuple, Dict, Any
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
import base58


class DIDKey:
    """
    Represents a did:key DID and associated Ed25519 keypair.
    
    Format: did:key:z6Mk<base58_public_key>
    
    The DID itself contains the public key, enabling offline verification.
    """
    
    PREFIX = "did:key:z6Mk"
    
    def __init__(self, private_key: ed25519.Ed25519PrivateKey):
        """
        Initialize DIDKey from a private key.
        
        Args:
            private_key: cryptography Ed25519PrivateKey instance
        """
        self._private_key = private_key
        self._public_key = private_key.public_key()
    
    @classmethod
    def generate(cls) -> "DIDKey":
        """
        Generate a new DIDKey with random keypair.
        
        Returns:
            New DIDKey instance with generated keys
        """
        private_key = ed25519.Ed25519PrivateKey.generate()
        return cls(private_key)
    
    @classmethod
    def from_private_key_bytes(cls, private_bytes: bytes) -> "DIDKey":
        """
        Reconstruct DIDKey from private key bytes.
        
        Args:
            private_bytes: 32 bytes of Ed25519 private key
            
        Returns:
            DIDKey instance
        """
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
        return cls(private_key)
    
    @classmethod
    def from_did(cls, did: str, private_key_bytes: bytes) -> "DIDKey":
        """
        Reconstruct DIDKey from DID string and private key bytes.
        
        Args:
            did: DID string (did:key:z6Mk...)
            private_key_bytes: 32 bytes of private key
            
        Returns:
            DIDKey instance
        """
        if not did.startswith(cls.PREFIX):
            raise ValueError(f"Invalid DID format: {did}")
        return cls.from_private_key_bytes(private_key_bytes)
    
    @property
    def did(self) -> str:
        """
        Get the DID identifier.
        
        Returns:
            DID string in format did:key:z6Mk<base58_pubkey>
        """
        public_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        base58_encoded = base58.b58encode(public_bytes).decode("ascii")
        return f"{self.PREFIX}{base58_encoded}"
    
    @property
    def public_key_bytes(self) -> bytes:
        """Get the public key as raw bytes (32 bytes for Ed25519)."""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    @property
    def public_key_base58(self) -> str:
        """Get the public key as base58-encoded string."""
        return base58.b58encode(self.public_key_bytes).decode("ascii")
    
    @property
    def private_key_bytes(self) -> bytes:
        """Get the private key as raw bytes (32 bytes for Ed25519)."""
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    def sign(self, data: bytes) -> bytes:
        """
        Sign data with the private key.
        
        Args:
            data: Bytes to sign
            
        Returns:
            64-byte Ed25519 signature
        """
        return self._private_key.sign(data)
    
    def verify(self, data: bytes, signature: bytes) -> bool:
        """
        Verify a signature.
        
        Args:
            data: Original data
            signature: 64-byte signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            self._public_key.verify(signature, data)
            return True
        except Exception:
            return False


class MessageSigner:
    """
    Handles signing and verification of messages using Ed25519.
    """
    
    @staticmethod
    def canonical_json(data: Dict[str, Any]) -> str:
        """
        Generate canonical JSON representation.
        
        Ensures deterministic output for signature verification:
        - No spaces after separators
        - Keys sorted alphabetically
        - No trailing newlines
        
        Args:
            data: Dictionary to serialize
            
        Returns:
            Canonical JSON string
        """
        return json.dumps(data, separators=(",", ":"), sort_keys=True)
    
    @staticmethod
    def sign_message(
        message_dict: Dict[str, Any],
        did_key: DIDKey
    ) -> str:
        """
        Sign a message dictionary.
        
        Args:
            message_dict: Message dict (must NOT contain 'signature' field)
            did_key: DIDKey instance for signing
            
        Returns:
            Base64-encoded signature string
        """
        canonical = MessageSigner.canonical_json(message_dict)
        signature_bytes = did_key.sign(canonical.encode("utf-8"))
        return base64.b64encode(signature_bytes).decode("ascii")
    
    @staticmethod
    def verify_message(
        message_dict: Dict[str, Any],
        signature_b64: str,
        from_did: str
    ) -> bool:
        """
        Verify a message signature.
        
        Args:
            message_dict: Message dict (without 'signature' field)
            signature_b64: Base64-encoded signature
            from_did: Sender DID (contains public key)
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Extract public key from DID
            if not from_did.startswith(DIDKey.PREFIX):
                return False
            
            base58_key = from_did[len(DIDKey.PREFIX):]
            public_key_bytes = base58.b58decode(base58_key)
            
            # Reconstruct public key
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            
            # Canonicalize message
            canonical = MessageSigner.canonical_json(message_dict)
            
            # Verify signature
            signature_bytes = base64.b64decode(signature_b64)
            public_key.verify(signature_bytes, canonical.encode("utf-8"))
            return True
        except Exception:
            return False


class SecurityError(Exception):
    """Raised when a security operation fails."""
    pass

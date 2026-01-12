"""Global constants for AIConexus"""

from enum import Enum

# Message Types
class MessageType(str, Enum):
    """Types of messages in the protocol"""

    QUERY = "QUERY"  # Discovery request
    OFFER = "OFFER"  # Response with offer
    EXECUTE = "EXECUTE"  # Execute request
    RESULT = "RESULT"  # Execution result
    ERROR = "ERROR"  # Error response
    ACK = "ACK"  # Acknowledgement
    HEARTBEAT = "HEARTBEAT"  # Health check


# Contract Status
class ContractStatus(str, Enum):
    """States of a contract"""

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


# Execution Status
class ExecutionStatus(str, Enum):
    """States of an execution"""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"


# Transaction Status
class TransactionStatus(str, Enum):
    """States of a transaction"""

    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


# Agent Status
class AgentStatus(str, Enum):
    """States of an agent"""

    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    BUSY = "BUSY"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"


# Defaults
DEFAULT_PROTOCOL_VERSION = "1.0"
DEFAULT_TIMEOUT_MS = 5000
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_RETRY_DELAY_MS = 100
DEFAULT_MAX_RETRY_DELAY_MS = 10000
DEFAULT_HEARTBEAT_INTERVAL_MS = 30000

# Limits
MAX_MESSAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
MAX_AGENTS = 1_000_000
MAX_CAPABILITIES_PER_AGENT = 1000
MAX_CONTRACT_DURATION_HOURS = 24 * 365  # 1 year

# Currency
DEFAULT_CURRENCY = "AIC"  # AIConexus token

# Performance SLA defaults
DEFAULT_SLA_LATENCY_MS = 100
DEFAULT_SLA_AVAILABILITY_PERCENT = 99.9
DEFAULT_SLA_TIMEOUT_MS = 5000

# Reputation
MIN_REPUTATION_SCORE = 0.0
MAX_REPUTATION_SCORE = 5.0
REPUTATION_UPDATE_INTERVAL_SECONDS = 60

# Logging
LOG_FORMAT_JSON = "json"
LOG_FORMAT_TEXT = "text"
DEFAULT_LOG_LEVEL = "INFO"

# Security
ENCRYPTION_ALGORITHM = "AES-256-GCM"
SIGNING_ALGORITHM = "SHA-256"
DEFAULT_KEY_SIZE_BITS = 2048
TOKEN_EXPIRATION_HOURS = 24

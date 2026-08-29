from enum import Enum


class Role(str, Enum):
    PRODUCER = "PRODUCER"
    FINANCE = "FINANCE"
    EDITOR = "EDITOR"
    CREATOR = "CREATOR"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class DecisionResult(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"

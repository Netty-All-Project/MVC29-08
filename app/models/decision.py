from dataclasses import dataclass
from .enums import DecisionResult


@dataclass
class Decision:
    request_id: str
    member_id: str
    result: DecisionResult

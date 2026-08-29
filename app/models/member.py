from dataclasses import dataclass
from .enums import Role


@dataclass
class Member:
    id: str
    name: str
    role: Role
    active: bool

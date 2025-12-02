from typing import Optional, Tuple

from pydantic import BaseModel, ConfigDict

class LoginSessionShort(BaseModel):
    Id: str
    User: Tuple[int, str]
    Remote: bool
    RemoteHost: Optional[str]
    RemoteUser: Optional[str]
    Service: Optional[str]
    Type: str
    Class: str
    Active: bool
    State: str
    Timestamp: int

    model_config = ConfigDict(populate_by_name=True)

class LoginSessionProperties(LoginSessionShort):
    Name: str
    TimestampMonotonic: int
    VTNr: int
    Seat: Tuple[str, str]
    TTY: Optional[str]
    Display: Optional[str]
    Desktop: Optional[str]
    Scope: Optional[str]
    Leader: int
    Audit: int
    IdleHint: bool
    IdleSinceHint: Optional[int]
    IdleSinceHintMonotonic: Optional[int]
    LockedHint: bool



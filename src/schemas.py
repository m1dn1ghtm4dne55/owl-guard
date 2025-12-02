from typing import Optional, Tuple

from pydantic import BaseModel, Field, ConfigDict

class LoginSessionShort(BaseModel):
    id: str = Field(alias='Id')
    name: str = Field(alias='Name')
    user: Tuple[int, str] = Field(alias='User')
    remote: bool = Field(alias='Remote')
    remote_host: Optional[str] = Field(alias='RemoteHost')
    service: Optional[str] = Field(alias='Service')
    type: str = Field(alias='Type')
    class_: str = Field(alias='Class')
    active: bool = Field(alias='Active')
    state: str = Field(alias='State')
    timestamp: int = Field(alias='Timestamp')

    model_config = ConfigDict(populate_by_name=True)

class LoginSessionProperties(LoginSessionShort):
    timestamp_monotonic: int = Field(alias='TimestampMonotonic')
    vtnr: int = Field(alias='VTNr')
    seat: Tuple[str, str] = Field(alias='Seat')
    tty: Optional[str] = Field(alias='TTY')
    display: Optional[str] = Field(alias='Display')
    desktop: Optional[str] = Field(alias='Desktop')
    remote_user: Optional[str] = Field(alias='RemoteUser')
    scope: Optional[str] = Field(alias='Scope')
    leader: int = Field(alias='Leader')
    audit: int = Field(alias='Audit')
    idle_hint: bool = Field(alias='IdleHint')
    idle_since_hint: Optional[int] = Field(alias='IdleSinceHint')
    idle_since_hint_monotonic: Optional[int] = Field(alias='IdleSinceHintMonotonic')
    locked_hint: bool = Field(alias='LockedHint')

from pydantic import BaseModel, Field, ConfigDict

class LoginSessionShort(BaseModel):
    id: str = Field(alias='Id')
    name: str = Field(alias='Name')
    user: tuple[int, str] = Field(alias='User')
    remote: bool = Field(alias='Remote')
    remote_host: str | None = Field(alias='RemoteHost')
    service: str | None = Field(alias='Service')
    type: str = Field(alias='Type')
    class_: str = Field(alias='Class')
    active: bool = Field(alias='Active')
    state: str = Field(alias='State')
    timestamp: int = Field(alias='Timestamp')

    model_config = ConfigDict(populate_by_name=True)

class LoginSessionProperties(LoginSessionShort):
    timestamp_monotonic: int = Field(alias='TimestampMonotonic')
    vtnr: int = Field(alias='VTNr')
    seat: tuple[str, str] = Field(alias='Seat')
    tty: str | None = Field(alias='TTY')
    display: str | None = Field(alias='Display')
    desktop: str | None = Field(alias='Desktop')
    remote_user: str | None = Field(alias='RemoteUser')
    scope: str | None = Field(alias='Scope')
    leader: int = Field(alias='Leader')
    audit: int = Field(alias='Audit')
    idle_hint: bool = Field(alias='IdleHint')
    idle_since_hint: int | None = Field(alias='IdleSinceHint')
    idle_since_hint_monotonic: int | None = Field(alias='IdleSinceHintMonotonic')
    locked_hint: bool = Field(alias='LockedHint')

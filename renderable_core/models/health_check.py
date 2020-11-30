from enum import Enum

from pydantic import Field

from . import Base


class Status(str, Enum):
  offline = 'offline'
  online = 'online'


class HealthCheckResponse(Base):
  version: str = Field(...)
  status: Status = Field(...)

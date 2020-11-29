from enum import Enum

from pydantic import Field

from . import Base


class ControlFrameType(str, Enum):
  ping = 'ping'
  pong = 'pong'


class ControlFrame(Base):
  type: ControlFrameType = Field(...)

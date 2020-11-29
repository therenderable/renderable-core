from pydantic import Field

from . import Base


class ErrorResponse(Base):
  detail: str = Field(...)

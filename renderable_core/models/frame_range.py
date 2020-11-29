from pydantic import validator, Field

from . import Base


class FrameRange(Base):
  start: int = Field(..., le = 1000000)
  end: int = Field(..., le = 1000000)

  @validator('end')
  def validate_range(cls, value, values):
    if value < values['start']:
      raise ValueError('invalid range')

    return value

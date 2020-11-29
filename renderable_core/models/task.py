from datetime import datetime
from typing import List, Optional

from pydantic import Field, HttpUrl

from .. import utils
from . import ObjectID, State, Base, FrameRange


class TaskDocument(Base):
  id: ObjectID = Field(default_factory = ObjectID, alias = '_id')
  job_id: ObjectID = Field(...)
  frame_range: FrameRange = Field(...)
  state: State = Field(...)
  retries: int = Field(..., ge = 0)
  image_urls: List[HttpUrl] = []
  created_at: datetime = Field(default_factory = utils.utc_now)
  updated_at: datetime = Field(default_factory = utils.utc_now)


class TaskMessage(Base):
  id: ObjectID = Field(...)
  job_id: ObjectID = Field(...)


class TaskRequest(Base):
  state: State = Field(...)


class TaskResponse(Base):
  id: ObjectID = Field(...)
  frame_range: FrameRange = Field(...)
  state: State = Field(...)
  image_urls: List[HttpUrl] = Field(...)
  created_at: datetime = Field(...)
  updated_at: datetime = Field(...)
  job: Optional['JobResponse'] = None


from .job import JobResponse


TaskResponse.update_forward_refs()

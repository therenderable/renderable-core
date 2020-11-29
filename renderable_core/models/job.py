from datetime import datetime
from typing import Optional, List

from pydantic import Field, HttpUrl

from .. import utils
from . import ObjectID, State, Action, Base, FrameRange


class JobDocument(Base):
  id: ObjectID = Field(default_factory = ObjectID, alias = '_id')
  task_ids: List[ObjectID] = Field(...)
  parallelism: int = Field(..., gt = 0, le = 64)
  container_name: str = Field(...)
  frame_range: FrameRange = Field(...)
  state: State = Field(...)
  scene_url: Optional[HttpUrl] = None
  sequence_url: Optional[HttpUrl] = None
  created_at: datetime = Field(default_factory = utils.utc_now)
  updated_at: datetime = Field(default_factory = utils.utc_now)


class JobMessage(Base):
  id: Optional[ObjectID] = None
  state: Optional[State] = None


class JobRequest(Base):
  parallelism: int = Field(4, gt = 0, le = 64)
  container_name: str = Field(...)
  frame_range: FrameRange = Field(...)


class JobActionRequest(Base):
  action: Action = Field(...)


class JobResponse(Base):
  id: ObjectID = Field(...)
  parallelism: int = Field(..., gt = 0, le = 64)
  container_name: str = Field(...)
  frame_range: FrameRange = Field(...)
  state: State = Field(...)
  scene_url: Optional[HttpUrl] = Field(...)
  sequence_url: Optional[HttpUrl] = Field(...)
  created_at: datetime = Field(...)
  updated_at: datetime = Field(...)
  tasks: Optional[List['TaskResponse']] = None


from .task import TaskResponse


JobResponse.update_forward_refs()

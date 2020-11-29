from datetime import datetime
from typing import Optional

from pydantic import Field

from .. import utils
from . import ObjectID, NodeType, Base


class DeviceDocument(Base):
  id: ObjectID = Field(default_factory = ObjectID, alias = '_id')
  node_type: NodeType = Field(...)
  joined_at: datetime = Field(default_factory = utils.utc_now)


class DeviceRequest(Base):
  node_type: NodeType = NodeType.worker


class DeviceResponse(Base):
  id: ObjectID = Field(...)
  node_type: NodeType = Field(...)
  token: Optional[str] = None
  joined_at: datetime = Field(...)

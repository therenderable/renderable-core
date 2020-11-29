from pydantic import Field, conlist

from . import ObjectID, State, Base


class ResourceDocument(Base):
  extensions: conlist(str, min_items = 1)
  content_types: conlist(str, min_items = 1)


class ResourceMessage(Base):
  job_id: ObjectID = Field(...)
  job_state: State = Field(...)

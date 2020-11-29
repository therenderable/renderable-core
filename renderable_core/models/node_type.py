from enum import Enum


class NodeType(str, Enum):
  manager = 'manager'
  worker = 'worker'

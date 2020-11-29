from enum import Enum


class State(str, Enum):
  ready = 'ready'
  running = 'running'
  done = 'done'
  error = 'error'

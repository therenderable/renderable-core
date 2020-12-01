import time
import signal
from threading import Thread


class Executor:
  def __init__(self):
    self.exiting = False
    self.atomic = False

    signal.signal(signal.SIGINT, self._exit)
    signal.signal(signal.SIGTERM, self._exit)

  def _exit(self, signum, frame):
    self.exiting = True

  def begin_atomic(self):
    self.atomic = True

  def end_atomic(self):
    self.atomic = False
    time.sleep(5)

  def run(self, task, *args, **kwargs):
    thread = Thread(target = task, args = args, kwargs = kwargs, daemon = True)
    thread.start()

    while not self.exiting or self.atomic:
      pass

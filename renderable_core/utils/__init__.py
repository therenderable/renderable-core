import datetime
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, ZipInfo
import asyncio
from functools import partial

import numpy as np


def utc_now():
  return datetime.datetime.now(datetime.timezone.utc)

def run_as_sync(coroutine, loop = None):
  if loop is None:
    loop = asyncio.get_event_loop()

  future = asyncio.run_coroutine_threadsafe(coroutine, loop)

  return future.result()

async def run_as_async(function, *args, **kwargs):
  loop = asyncio.get_running_loop()
  partial_function = partial(function, *args, **kwargs)

  return await loop.run_in_executor(None, partial_function)

def get_file_extension(filename):
  filename = Path(filename)

  return filename.suffix

def unit_prefix(value, prefix_name):
  prefixes = {
    'y': 1e-24,
    'z': 1e-21,
    'a': 1e-18,
    'f': 1e-15,
    'p': 1e-12,
    'n': 1e-9,
    'u': 1e-6,
    'm': 1e-3,
    'c': 1e-2,
    'd': 1e-1,
    'k': 1e3,
    'M': 1e6,
    'G': 1e9,
    'T': 1e12,
    'P': 1e15,
    'E': 1e18,
    'Z': 1e21,
    'Y': 1e24
  }

  return value * prefixes[prefix_name]

def compress_files(files):
  zip_data = BytesIO()

  with ZipFile(zip_data, 'w') as zip_file:
    for filename, data in files:
      metadata = ZipInfo(filename)
      zip_file.writestr(metadata, data.getvalue())

  zip_data.seek(0)

  return zip_data

def group_frames(start, end, parallelism):
  end = end + 1

  frame_count = end - start
  parallelism = min(frame_count, parallelism)
  frame_batch = round(frame_count / parallelism)

  frames = np.arange(start, end)
  groups = np.split(frames, np.arange(frame_batch, len(frames), frame_batch))

  return [group.tolist() for group in groups]

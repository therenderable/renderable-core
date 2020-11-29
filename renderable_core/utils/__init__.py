import datetime
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, ZipInfo
import asyncio
from functools import partial

import numpy as np


def utc_now():
  return datetime.datetime.now(datetime.timezone.utc)

def run_as_sync(coroutine, loop):
  future = asyncio.run_coroutine_threadsafe(coroutine, loop)

  return future.result()

async def run_as_async(function, *args, **kwargs):
  loop = asyncio.get_running_loop()
  partial_function = partial(function, *args, **kwargs)

  return await loop.run_in_executor(None, partial_function)

def get_file_extension(filename):
  filename = Path(filename)

  return filename.suffix

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

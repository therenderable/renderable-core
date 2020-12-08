import datetime
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, ZipInfo
import asyncio
from functools import partial

import numpy as np
from tabulate import tabulate

from ..models import State


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

def job_statistics(jobs):
  def filter_by_completed(job):
    return job.state == State.done or job.state == State.error

  def format_job(job):
    task_count = len(job.tasks)
    completed_count = len(list(filter(filter_by_completed, job.tasks)))
    completed_percentage = completed_count / task_count * 100 if task_count > 0 else 0

    progress = f'{completed_percentage:.2f}%'
    frame_range = f'{job.frame_range.start} - {job.frame_range.end}'
    sequence = '-' if job.sequence_url is None else job.sequence_url

    datetime_format = '%x %X'

    created_at = job.created_at.strftime(datetime_format)
    updated_at = job.updated_at.strftime(datetime_format)

    return [job.id, job.state, progress, job.container_name, frame_range,
      job.parallelism, sequence, created_at, updated_at]

  headers = ['ID', 'State', 'Progress', 'Container Name', 'Frame Range',
    'Parallelism', 'Sequence', 'Created At', 'Updated At']

  data = list(map(format_job, jobs))

  table = tabulate(data, headers = headers, stralign = 'center', numalign = 'center')

  return str(table)

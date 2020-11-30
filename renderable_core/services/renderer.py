from string import Template
from pathlib import Path
import subprocess
import shutil

import psutil


class RubyTemplate(Template):
  delimiter = '#'


class Renderer:
  def __init__(self, command_template, temporary_directory, cache_factor):
    self.command_template = command_template
    self.temporary_directory = temporary_directory
    self.cache_factor = cache_factor

  def path_from_id(self, id, prefix):
    return Path(f'{self.temporary_directory}/{prefix}/{id}')

  def has_cache(self, task):
    path = self.path_from_id(task.job.id, 'jobs')
    has_files = len(list(path.glob('*'))) > 0 if path.is_dir() else False

    return has_files

  def delete_cache(self, task):
    task_path = self.path_from_id(task.id, 'tasks')

    if task_path.is_dir():
      shutil.rmtree(task_path)

    jobs_path = self.path_from_id('', 'jobs')

    if jobs_path.is_dir():
      disk_usage = psutil.disk_usage(jobs_path)

      if disk_usage.percent > self.cache_factor:
        shutil.rmtree(jobs_path)

  def render(self, task):
    scene_path = str(next(self.path_from_id(task.job.id, 'jobs').glob('*')).resolve())
    sequence_path = str(self.path_from_id(task.id, 'tasks').resolve())

    sequence_path += '/'

    command = RubyTemplate(self.command_template).substitute(
      scene_path = scene_path,
      sequence_path = sequence_path,
      frame_start = task.frame_range.start,
      frame_end = task.frame_range.end)

    import logging
    logger = logging.getLogger('renderable-box')
    logger.setLevel(logging.INFO)

    logger.info(scene_path)
    logger.info(sequence_path)
    logger.info(command)
    logger.info(list(self.path_from_id(task.job.id, 'jobs').glob('*')))

    subprocess.check_call(command, shell = True)

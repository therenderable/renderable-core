import os
from pathlib import Path
import json

import requests
import websockets

from .. import utils
from ..models import Action, ControlFrameType, ControlFrame, DeviceRequest, DeviceResponse, \
  JobRequest, JobActionRequest, JobResponse, TaskRequest, TaskResponse


class APIClient:
  def __init__(self, hostname, port, version, secure, access_key = None, temporary_directory = None):
    self.hostname = hostname
    self.port = port
    self.version = version
    self.secure = secure
    self.access_key = access_key
    self.temporary_directory = temporary_directory

    protocol = 'https' if self.secure else 'http'

    self.base_url = f'{protocol}://{self.hostname}:{self.port}/{self.version}'

    self.authentication_header = {
      'x-api-key': access_key
    }

  def _url_from_path(self, path):
    return f'{self.base_url}/{path}'

  def _filename_from_resource_url(self, url, prefix):
    id, filename = url.split('/')[-2:]

    return self.temporary_directory / Path(f'{prefix}/{id}/{filename}')

  def _path_from_id(self, id, prefix):
    return self.temporary_directory / Path(f'{prefix}/{id}')

  def register_device(self, node_type):
    url = self._url_from_path('devices/')

    device = DeviceRequest(node_type = node_type)

    response = requests.post(url, json = device.dict())
    response.raise_for_status()

    return DeviceResponse(**response.json())

  def get_device(self, id):
    url = self._url_from_path(f'devices/{id}')

    response = requests.get(url)
    response.raise_for_status()

    return DeviceResponse(**response.json())

  def create_job(self, job):
    url = self._url_from_path('jobs/')

    response = requests.post(url, json = job.dict())
    response.raise_for_status()

    return JobResponse(**response.json())

  def upload_job_scene(self, id, scene_path):
    url = self._url_from_path(f'jobs/{id}')

    files = { 'scene': (scene_path.name, open(scene_path, 'rb')) }

    response = requests.post(url, files = files)
    response.raise_for_status()

    return JobResponse(**response.json())

  def update_job_state(self, id, action):
    url = self._url_from_path(f'jobs/{id}')

    job_action = JobActionRequest(action = action)

    response = requests.post(url, json = job_action.dict())
    response.raise_for_status()

    return JobResponse(**response.json())

  def submit_job(self, job, scene_path):
    job_response = self.create_job(job)
    job_response = self.upload_job_scene(job_response.id, scene_path)

    return self.update_job_state(job_response.id, Action.start)

  def listen_job(self, id, callback, timeout = 60):
    url = self._url_from_path(f'jobs/{id}/ws').replace('http', 'ws')

    async def process_message():
      async with websockets.connect(url, ping_interval = None, close_timeout = timeout) as websocket:
        while True:
          data = await websocket.recv()
          json_data = json.loads(data)

          try:
            response = ControlFrame(**json_data)
          except:
            response = JobResponse(**json_data)

          if isinstance(response, ControlFrame):
            pong_frame = ControlFrame(type = ControlFrameType.pong)
            await websocket.send(pong_frame.json())
          else:
            callback(response)

    utils.run_as_sync(process_message())

  def get_task(self, id):
    url = self._url_from_path(f'tasks/{id}')

    response = requests.get(url, headers = self.authentication_header)
    response.raise_for_status()

    return TaskResponse(**response.json())

  def update_task_state(self, task, state):
    url = self._url_from_path(f'tasks/{task.id}')

    task = TaskRequest(state = state)

    response = requests.post(url, headers = self.authentication_header, json = task.dict())
    response.raise_for_status()

    task_response = TaskResponse(**response.json())

    return task.state == task_response.state

  def download_task_resource(self, task):
    url = task.job.scene_url

    response = requests.get(url)
    response.raise_for_status()

    filename = self._filename_from_resource_url(url, 'jobs')

    os.makedirs(filename.parent, exist_ok = True)

    with open(filename, 'wb') as file:
      file.write(response.content)

    return filename

  def upload_task_resources(self, task):
    url = self._url_from_path(f'tasks/{task.id}/images')

    path = self._path_from_id(task.id, 'tasks')
    filenames = path.glob('*')

    images = [('images', (filename.name, open(filename, 'rb'))) for filename in filenames]

    response = requests.post(url, headers = self.authentication_header, files = images)
    response.raise_for_status()

    return TaskResponse(**response.json())

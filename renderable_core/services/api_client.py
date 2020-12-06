import os
from pathlib import Path

import requests

from ..models import DeviceRequest, DeviceResponse, TaskRequest, TaskResponse


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

  def url_from_path(self, path):
    return f'{self.base_url}/{path}'

  def filename_from_resource_url(self, url, prefix):
    id, filename = url.split('/')[-2:]

    return self.temporary_directory / Path(f'{prefix}/{id}/{filename}')

  def path_from_id(self, id, prefix):
    return self.temporary_directory / Path(f'{prefix}/{id}')

  def register_device(self, node_type):
    url = self.url_from_path(f'devices/')

    device = DeviceRequest(node_type = node_type)

    response = requests.post(url, json = device.dict())
    response.raise_for_status()

    return DeviceResponse(**response.json())

  def get_device(self, id):
    url = self.url_from_path(f'devices/{id}')

    response = requests.get(url)
    response.raise_for_status()

    return DeviceResponse(**response.json())

  def get_task(self, id):
    url = self.url_from_path(f'tasks/{id}')

    response = requests.get(url, headers = self.authentication_header)
    response.raise_for_status()

    return TaskResponse(**response.json())

  def update_task_state(self, task, state):
    url = self.url_from_path(f'tasks/{task.id}')

    task = TaskRequest(state = state)

    response = requests.post(url, headers = self.authentication_header, json = task.dict())
    response.raise_for_status()

    task_response = TaskResponse(**response.json())

    return task.state == task_response.state

  def download_task_resource(self, task):
    url = task.job.scene_url

    response = requests.get(url)
    response.raise_for_status()

    filename = self.filename_from_resource_url(url, 'jobs')

    os.makedirs(filename.parent, exist_ok = True)

    with open(filename, 'wb') as file:
      file.write(response.content)

    return filename

  def upload_task_resources(self, task):
    url = self.url_from_path(f'tasks/{task.id}/images')

    path = self.path_from_id(task.id, 'tasks')
    filenames = path.glob('*')

    images = [('images', (filename.name, open(filename, 'rb'))) for filename in filenames]

    response = requests.post(url, headers = self.authentication_header, files = images)
    response.raise_for_status()

    return TaskResponse(**response.json())

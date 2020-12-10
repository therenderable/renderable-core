import time
from threading import Thread, Lock

import docker


class Autoscaler:
  def __init__(self, hostname, port, certificate_path, cleanup_period, cooldown_period):
    self.hostname = hostname
    self.port = port
    self.certificate_path = certificate_path
    self.cleanup_period = cleanup_period
    self.cooldown_period = cooldown_period

    public_certificate_path = str(self.certificate_path / 'cert.pem')
    private_certificate_path = str(self.certificate_path / 'key.pem')

    tls_config = docker.tls.TLSConfig(
      client_cert = (public_certificate_path, private_certificate_path))

    self.client = docker.DockerClient(f'https://{self.hostname}:{self.port}', tls = tls_config)

    self.requests = {}
    self.requests_lock = Lock()

    cleanup_thread = Thread(target = self._cleanup_nodes, daemon = True)
    cleanup_thread.start()

    scaling_thread = Thread(target = self._scale_services, daemon = True)
    scaling_thread.start()

  def _cleanup_nodes(self):
    def filter_by_status(node):
      return node.attrs['Status']['State'] == 'down'

    while True:
      try:
        nodes = list(filter(filter_by_status, self.client.nodes.list()))

        for node in nodes:
          node.remove(force = True)
      except:
        pass

      time.sleep(self.cleanup_period)

  def _scale_services(self):
    while True:
      self.requests_lock.acquire()

      for container_name, delta in self.requests.items():
        if delta != 0:
          try:
            self._update_service(container_name, delta)
            self.requests[container_name] = 0
          except:
            pass

      self.requests_lock.release()

      time.sleep(self.cooldown_period)

  def _update_service(self, container_name, delta):
    service = self.client.services.get(container_name)

    replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
    target_replicas = int(max(replicas + delta, 0))

    service.scale(target_replicas)

  def scale(self, container_name, task_count, upscaling):
    self.requests_lock.acquire()

    if container_name not in self.requests.keys():
      self.requests[container_name] = 0

    delta = task_count if upscaling else -task_count

    self.requests[container_name] += delta

    self.requests_lock.release()

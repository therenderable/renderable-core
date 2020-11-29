from datetime import datetime

import docker


class Autoscaler:
  def __init__(self, hostname, port, certificate_path, cooldown_period):
    self.hostname = hostname
    self.port = port
    self.certificate_path = certificate_path
    self.cooldown_period = cooldown_period

    public_certificate_path = str(self.certificate_path / 'cert.pem')
    private_certificate_path = str(self.certificate_path / 'key.pem')

    tls_config = docker.tls.TLSConfig(
      client_cert = (public_certificate_path, private_certificate_path))

    self.client = docker.DockerClient(f'https://{self.hostname}:{self.port}', tls = tls_config)

  def scale(self, container_name, task_count, upscaling):
    service = self.client.services.get(container_name)

    last_updated_time = datetime.fromisoformat(service.attrs['UpdatedAt'][:26])
    last_update_period = (datetime.utcnow() - last_updated_time).total_seconds()

    assert last_update_period > self.cooldown_period

    delta = task_count if upscaling else -task_count

    replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']
    target_replicas = int(max(replicas + delta, 0))

    service.scale(target_replicas)

from enum import Enum

import requests
import docker

from .. import utils


class ClusterStatus(int, Enum):
  node_already_initialized = 503
  resource_already_exists = 409


class Cluster:
  def __init__(self,
      domain_ip, hostname, port, manager_port, certificate_path,
      registry_domain, secure_registry_domain, registry_username, registry_password,
      secrets, environment):
    self.domain_ip = domain_ip
    self.hostname = hostname
    self.port = port
    self.manager_port = manager_port
    self.certificate_path = certificate_path
    self.registry_domain = registry_domain
    self.secure_registry_domain = secure_registry_domain
    self.registry_username = registry_username
    self.registry_password = registry_password
    self.secrets = secrets
    self.environment = environment

    protocol = 'https' if self.secure_registry_domain else 'http'
    self.registry_base_url = f'{protocol}://{self.registry_domain}/v2'

    public_certificate_path = str(self.certificate_path / 'cert.pem')
    private_certificate_path = str(self.certificate_path / 'key.pem')

    tls_config = docker.tls.TLSConfig(
      client_cert = (public_certificate_path, private_certificate_path))

    self.client = docker.DockerClient(f'https://{self.hostname}:{self.port}', tls = tls_config)

    self._initialize()
    self._drain_manager()
    self._register_secrets()
    self._login_registry()

  def _initialize(self):
    try:
      self.client.swarm.init(
        advertise_addr = self.domain_ip,
        listen_addr = f'0.0.0.0:{self.manager_port}',
        dispatcher_heartbeat_period = int(utils.unit_prefix(120, 'G')))
    except docker.errors.APIError as error:
      if error.status_code != ClusterStatus.node_already_initialized:
        raise error

  def _drain_manager(self):
    info = self.client.info()

    node_id = info['Swarm']['NodeID']

    request = {
      'Role': 'manager',
      'Availability': 'drain'
    }

    node = self.client.nodes.get(node_id)
    node.update(request)

  def _register_secrets(self):
    for name, data in self.secrets.items():
      secret = {
        'name': name.lower(),
        'data': data.encode('utf-8')
      }

      try:
        self.client.secrets.create(**secret)
      except docker.errors.APIError as error:
        if error.status_code != ClusterStatus.resource_already_exists:
          raise error

  def _login_registry(self):
    self.client.login(self.registry_username, self.registry_password, registry = self.registry_base_url)

  def get_address(self):
    return f'{self.domain_ip}:{self.manager_port}'

  def get_container_names(self):
    request = requests.get(f'{self.registry_base_url}/_catalog', auth = (self.registry_username, self.registry_password))
    request.raise_for_status()

    response = request.json()
    containers = response['repositories']

    return containers

  def create_service(self, container_name):
    secrets = [docker.types.SecretReference(secret.id, secret.name) for secret in self.client.secrets.list()]
    environment_variables = [f'{name}={value}' for name, value in self.environment.items()]

    resources = docker.types.Resources(
      cpu_reservation = int(utils.unit_prefix(2, 'G')),
      cpu_limit = int(utils.unit_prefix(4, 'G')),
      mem_reservation = int(utils.unit_prefix(2, 'G')),
      mem_limit = int(utils.unit_prefix(4, 'G')))

    service = {
      'name': container_name,
      'image': f'{self.registry_domain}/{container_name}:latest',
      'mode': docker.types.ServiceMode(mode = 'replicated', replicas = 0),
      'resources': resources,
      'secrets': secrets,
      'env': environment_variables,
      'stop_grace_period': int(utils.unit_prefix(48 * 3600, 'G'))
    }

    try:
      self.client.services.create(**service)
    except docker.errors.APIError as error:
      if error.status_code != ClusterStatus.resource_already_exists:
        raise error

  def join(self, device):
    self.client.swarm.reload()

    node_type = device['node_type'].capitalize()

    return self.client.swarm.attrs['JoinTokens'][node_type]

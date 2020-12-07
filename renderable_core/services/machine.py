import json
import platform
import subprocess


class Machine:
  def __init__(self, name, path):
    self.name = name
    self.path = path

    executable_intermediate_path = self.path / 'bin'

    self.executable = executable_intermediate_path / 'docker-machine'

  def _command_from_args(self, args):
    return f'{self.executable} --storage-path {self.path} {args}'

  def list_machines(self):
    command = self._command_from_args('ls')

    output = subprocess.check_output(command, shell = True).decode().strip().split('\n')

    attributes = [name.lower() for name in output[0].split()[:5]]
    values = [value.split()[:5] for value in output[1:]]

    return [{attributes[index]: item.lower() for index, item in enumerate(value)} for value in values]

  def exists(self):
    def get_name(machine):
      return machine['name']

    machines = self.list_machines()
    machine_names = list(map(get_name, machines))

    return self.name in machine_names

  def running(self):
    def filter_by_name(machine):
      return machine['name'] == self.name

    machines = self.list_machines()
    machine = next(filter(filter_by_name, machines), None)

    if machine is None:
      return False

    return machine['state'] == 'running'

  def create(self, cpus, memory, storage):
    driver = 'hyperv' if platform.system() == 'Windows' else 'virtualbox'
    extra_args = '--hyperv-virtual-switch "Default Switch"' if driver == 'hyperv' else ''

    create_command = self._command_from_args(
      f'create --driver {driver} --{driver}-cpu-count {cpus} --{driver}-memory {memory} --{driver}-disk-size {storage} {extra_args} {self.name}')

    subprocess.check_call(create_command, shell = True)

  def remove(self):
    command = self._command_from_args(f'rm {self.name}')
    subprocess.check_call(command, shell = True)

  def inspect(self):
    command = self._command_from_args(f'inspect {self.name}')
    output = subprocess.check_output(command, shell = True)

    return json.loads(output)

  def update(self, cpus, memory, storage, force = False):
    if force:
      update = True
    else:
      machine = self.inspect()

      update_cpus = machine['Driver']['CPU'] != cpus
      update_memory = machine['Driver']['MemSize'] != memory
      update_storage = machine['Driver']['DiskSize'] != storage

      update = update_cpus or update_memory or update_storage

    if update:
      if self.running():
        self.stop()

      self.remove()
      self.create(cpus, memory, storage)

    if not self.running():
      self.start()

  def start(self):
    command = self._command_from_args(f'start {self.name}')
    subprocess.check_call(command, shell = True)

  def stop(self):
    command = self._command_from_args(f'stop {self.name}')
    subprocess.check_call(command, shell = True)

  def join_cluster(self, cluster_address, token):
    command = self._command_from_args(f'ssh {self.name} docker swarm join --token {token} {cluster_address}')
    subprocess.check_call(command, shell = True)

  def leave_cluster(self):
    command = self._command_from_args(f'ssh {self.name} docker swarm leave')
    subprocess.check_call(command, shell = True)

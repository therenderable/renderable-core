import os


class Configuration:
  def __init__(self, secret_path):
    self.secret_path = secret_path

    self.secrets = {}

    secret_filenames = self.secret_path.rglob('*')

    for filename in secret_filenames:
      with open(filename, 'r') as file:
        value = file.read().strip()

      name = filename.name.upper()
      self.secrets[name] = value

  def get(self, name):
    return self.secrets.get(name) or os.environ.get(name)

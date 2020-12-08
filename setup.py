from distutils.util import convert_path
from setuptools import setup, find_packages


package_name = 'renderable-core'

package_directory = package_name.replace('-', '_')
package_info = {}

with open(convert_path(f'{package_directory}/package.py'), 'r') as file:
  exec(file.read(), package_info)

requirements = [
  'numpy>=1.19.0',
  'psutil>=5.7.0',
  'requests>=2.25.0',
  'websockets>=8.0',
  'pydantic>=1.7.0',
  'docker>=4.3.0',
  'pymongo>=3.11.0',
  'minio>=6.0.0',
  'pika>=1.1.0'
]

setup(
  name = package_name,
  version = package_info['__version__'],
  description = package_info['__description__'],
  author = package_info['__author__'],
  author_email = package_info['__email__'],
  license = package_info['__license__'],
  python_requires = '>=3.7.0',
  install_requires = requirements,
  packages = find_packages(),
  zip_safe = False)

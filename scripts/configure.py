###############################################################################
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
###############################################################################

# Builtin Imports
import subprocess

# Third Party Imports
from jinja2 import Environment, FileSystemLoader

# Cloudify Imports
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError

# Constants
CONFIG_PATH = '/etc/haproxy/haproxy.cfg'
TEMPLATE_FOLDER = 'templates'
TEMPLATE_FILE_NAME = 'haproxy.cfg.template'

env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
template = env.get_template(TEMPLATE_FILE_NAME)

ctx.logger.info('Configuring HAProxy.')
ctx.logger.debut('Building a dict object that will contain variables '
                 'to write to the Jinja2 template.')

config = dict()
config['global_maxconn'] = ctx.instance.properties['global_maxconn']
config['mode'] = ctx.instance.properties['mode']
config['timeout_connect'] = ctx.instance.properties['timeout_connect']
config['timeout_client'] = ctx.instance.properties['timeout_client']
config['timeout_server'] = ctx.instance.properties['timeout_server']
config['frontend_id'] = ctx.instance.id
config['frontend_port'] = ctx.instance.properties['port']
config['default_backend'] = ctx.instance.properties['default_backend']
config['backends'] = ctx.node.runtime_properties['backends']

for client in config['backends']:
    config[client]['address'] = ctx.node.runtime_properties[client]['address']
    config[client]['port'] = ctx.node.runtime_properties[client]['port']
    config[client]['maxconn'] = ctx.node.runtime_properties[client]['maxconn']

ctx.logger.debug('Rendering the Jinja2 template to {0}.'.format(CONFIG_PATH))

try:
    with open(CONFIG_PATH, 'w') as file:
        file.write(template.render(config))
        file.close()
except IOError:
    raise NonRecoverableError(
        'Permission denied: {0}.'.format(CONFIG_PATH))

test_config = subprocess.Popen(
    ['sudo', '/usr/sbin/haproxy', '-f', CONFIG_PATH, '-c'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)
output = test_config.communicate()

ctx.logger.debug('Config Validation: {0}'.format(output))

if test_config.returncode != 0:
    raise NonRecoverableError('Failed to Configure')
else:
    ctx.logger.info('Configure was successful.')

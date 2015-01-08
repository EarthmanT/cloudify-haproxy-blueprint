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

# Cloudify Imports
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError

# Constants
CONFIG_PATH = '/etc/haproxy/haproxy.cfg'


ctx.logger.info('Configuring HAProxy.')

ctx.logger.debug('Creating the global config section.')

global_config = 'global\n'\
                '\t{0}\n'\
                '\t{1} {2}'.format('daemon', 'maxconn',
                                   ctx.source.node.properties['maxconn'])

ctx.logger.debug('Creating the defaults config section.')

default_config = ('defaults\n'
                  '\tmode {0}\n'
                  '\ttimeout connect {1}\n'
                  '\ttimeout client {2}\n'
                  '\ttimeout server {3}\n').format(
    ctx.source.node.properties['mode'],
    ctx.source.node.properties['timeout_connect'],
    ctx.source.node.properties['timeout_client'],
    ctx.source.node.properties['timeout_server'])

ctx.logger.debug('Creating the frontend config section.')

frontend_config = ('frontend {1}\n'
                   '\tbind *:{3}\n'
                   '\tdefault_backend {4}\n').format(
    ctx.source.instance.id, str(ctx.source.node.properties['port']),
    ctx.source.node.properties['default_backend'])

ctx.logger.debug('Creating the backend config section.')

backend_config = 'backend {1}\n'.format(
    ctx.source.node.properties['default_backend'])

for relationship in ctx.instance.relationships:
    if relationship.type == 'node_connected_to_backend':
        string = 'server\t{0} {1} {2}:{3} maxconn {4}\n'.format(
            ctx.source.node.id,
            relationship.target.node.properties['backend_address'],
            str(relationship.target.node.properties['port']),
            int(relationship.target.node.properties['maxconn']))
        backend_config = backend_config + string

ctx.logger.debug('Putting all of the config sections together.')

ctx.instance.runtime_properties['configuration'] = '{0}{1}{2}{3}'.format(
    global_config, default_config, frontend_config, backend_config)

ctx.logger.debug('Starting to write to {0}.'.format(CONFIG_PATH))

try:
    with open(CONFIG_PATH, 'w') as file:
        file.write(ctx.instance.runtime_properties['configuration'])
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

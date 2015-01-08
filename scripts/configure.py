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


def create_global_config(ctx):

    ctx.logger.debug('Creating the global config section.')

    string = 'global\n'
    if ctx.node.properties['daemon']:
        string = '{0}\t{1}\n'.format(string, 'daemon')
    string = '{0}\t{1} {2}'.format(
        string, 'maxconn', ctx.node.properties['maxconn'])

    ctx.instance.runtime_properties['global_config'] = string


def create_defaults_config(ctx):

    ctx.logger.debug('Creating the defaults config section.')

    string = 'defaults\n'
    string = '{0}\t{1} {2}\n'.format(
        string, 'mode', ctx.node.properties['mode'])
    string = '{0}\t{1} {2} {3}ms\n'.format(
        string, 'timeout', 'connect', ctx.node.properties['timeout_connect'])
    string = '{0}\t{1} {2} {3}ms\n'.format(
        string, 'timeout', 'client', ctx.node.properties['timeout_client'])
    string = '{0}\t{1} {2} {3}ms\n'.format(
        string, 'timeout', 'server', ctx.node.properties['timeout_server'])

    ctx.instance.runtime_properties['default_config'] = string


def create_frontend_config(ctx):

    ctx.logger.debug('Creating the frontend config section.')

    string = '{0} {1}\n'.format('frontend', ctx.instance.id)
    string = '{0}\t{1} *:{2}\n'.format(
        string, 'bind', str(ctx.node.properties['port']))
    string = '{0}\t{1} {2}\n'.format(
        string, 'default_backend', ctx.node.properties['default_backend'])

    ctx.instance.runtime_properties['frontend_config'] = string


def create_backend_config(ctx):

    ctx.logger.debug('Creating the backend config section.')

    string = '{0} {1}\n'.format(
        'backend', ctx.node.properties['default_backend'])
    for relationship in ctx.instance.relationships:
        if relationship.type == 'node_connected_to_backend':
            string = '{0}\t{1} {2} {3}:{4} {5} {6}\n'.format(
                string, 'server', ctx.source.node.id,
                relationship.target.node.properties['backend_address'],
                str(relationship.target.node.properties['port']), 'maxconn',
                relationship.target.node.properties['maxconn'], str(32))

    ctx.instance.runtime_properties['backend_config'] = string


def create_config(ctx):

    create_global_config(ctx=ctx)
    create_defaults_config(ctx=ctx)
    create_frontend_config(ctx=ctx)
    create_backend_config(ctx=ctx)

    ctx.logger.debug('Putting all of the config sections together.')

    ctx.instance.runtime_properties['configuration'] = '{0}{1}{2}{3}'.format(
        ctx.instance.runtime_properties['global_config'],
        ctx.instance.runtime_properties['default_config'],
        ctx.instance.runtime_properties['frontend_config'],
        ctx.instance.runtime_properties['backend_config'])


def write_config(ctx):

    ctx.logger.debug('Starting to write to {0}.'.format(CONFIG_PATH))

    try:
        with open(CONFIG_PATH, 'w') as file:
            file.write(ctx.instance.runtime_properties['configuration'])
            file.close()
    except IOError:
        raise NonRecoverableError(
            'Permission denied: {0}.'.format(CONFIG_PATH))

ctx.logger.info('Configuring HAProxy.')

create_config(ctx=ctx)
write_config(ctx=ctx)

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

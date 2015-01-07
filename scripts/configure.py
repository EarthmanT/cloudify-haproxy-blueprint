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
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


def create_global_config(ctx):

    string = 'global\n'
    if ctx.node.properties['daemon']:
        string = '{0}\t{1}'.format(string, 'daemon')
    string = '{0}\t{1} {2}'.format(
        string, 'daemon', ctx.node.properties['maxconn'])

    return string


def create_defaults(ctx):

    string = 'defaults\n'
    string = '{0}\t{1} {2}\n'.format(
        string, 'mode', ctx.node.properties['http'])
    string = '{0}\t{1} {2} {3}ms\n'.format(
        string, 'timeout', 'connect', ctx.node.properties['timeout_connect'])
    string = '{0}\t{1} {2} {3}ms\n'.format(
        string, 'timeout', 'client', ctx.node.properties['timeout_client'])
    string = '{0}\t{1} {2} {3}ms\n'.format(
        string, 'timeout', 'server', ctx.node.properties['timeout_server'])

    return '{0}\n'.format(string)


def create_frontend(ctx):

    string = '{0} {1}\n'.format('frontend', ctx.instance.id)
    string = '{0}\t{1} *:{2}\n'.format(
        string, 'bind', str(ctx.node.properties['port']))
    string = '{0}\t{1} {2}\n'.format(
        string, 'default_backend', ctx.node.properties['default_backend'])

    return '{0}\n'.format(string)


def create_backend(ctx):

    string = '{0} {1}\n'.format(
        'backend', ctx.node.properties['default_backend'])
    for relationship in ctx.node.relationships:
        string = '{0}\t{1} {2} {3}:{4} {5} {6}\n'.format(
            string, 'server', ctx.source.node.id,
            ctx.source.node.properties['backend_address'],
            str(ctx.source.node.properties['port']), 'maxconn',
            ctx.source.node.properties['maxconn'], str(32))

    return '{0}\n'.format(string)


@operation
def configure(**kwargs):

    config_path = '/etc/haproxy/haproxy.cfg'

    ctx.logger.info('Configuring HAProxy')

    blob = '{0}{1}{2}{3}'.format(
        create_global_config(ctx=ctx),
        create_defaults(ctx=ctx),
        create_frontend(ctx=ctx),
        create_backend(ctx=ctx))

    with open(config_path, 'w') as file:
        file.write(blob)
        file.close()

    test_config = subprocess.Popen(
        ['/usr/sbin/haproxy', '-f', config_path, '-c'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output = test_config.communicate()

    ctx.logger.debug('Config Validation: {0}'.format(output))

    if test_config.returncode != 0:
        raise NonRecoverableError('Failed to Configure')
    else:
        ctx.logger.info('Configure was successful.')

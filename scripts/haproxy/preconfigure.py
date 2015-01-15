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

# Third Party Imports

# Cloudify Imports
from cloudify import ctx
from cloudify.state import ctx_parameters as inputs

# Constants

ctx.logger.debug('Creating a configuration for Relationship: {0}.'.format(
    ctx.source.instance.id))

name = ctx.target.instance.id

if 'backend_names' in ctx.source.instance.runtime_properties:
    ctx.source.instance.runtime_properties['backend_names'].append(name)
    ctx.source.instance.runtime_properties[name] = {
        'address': inputs['backend_address'],
        'port': str(inputs['port']),
        'maxconn': int(inputs['maxconn'])
    }
else:
    ctx.source.instance.runtime_properties['backend_names'] = []
    ctx.source.instance.runtime_properties['backend_names'].append(name)
    ctx.source.instance.runtime_properties[name] = {
        'address': inputs['backend_address'],
        'port': str(inputs['port']),
        'maxconn': int(inputs['maxconn'])
    }

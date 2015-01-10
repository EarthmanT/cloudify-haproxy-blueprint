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

# Constants

ctx.logger.debug('Creating a configuration for Relationship: {0}.'.format(
    ctx.relationship.instance))

ctx.relationship.target.runtime_properties['backends'] = {
    ctx.source.node.id: {
        'backend': ctx.source.node.id,
        'address': ctx.relationship.source.node.properties['backend_address'],
        'port': str(ctx.relationship.source.node.properties['port']),
        'maxconn': int(ctx.relationship.source.node.properties['maxconn'])
    }
}

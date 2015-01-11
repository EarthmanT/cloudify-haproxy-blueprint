########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.


import os
import unittest

from cloudify.workflows import local


class TestPlugin(unittest.TestCase):

    def setUp(self):
        # build blueprint path
        blueprint_path = os.path.join(os.path.dirname(__file__),
                                      '..', 'blueprint.yaml')
        # inject input from test
        inputs = {
            'agent_public_key_name': 'trammell-agent-kp',
            'agent_user': 'ubuntu',
            'frontend_image_name': 'Ubuntu Server 12.04.2 LTS'
                                   ' (amd64 20130318) - Partner Image',
            'frontend_flavor_name': 'standard.medium',
            'backend_image_name': 'Ubuntu Server 12.04.2 LTS '
                                  '(amd64 20130318) - Partner Image',
            'backend_flavor_name': 'standard.medium',
            'backend_app_port': 8000
        }

        # setup local workflow execution environment
        self.env = local.init_env(blueprint_path,
                                  name=self.test_install_workflow,
                                  inputs=inputs)

    def test_install_workflow(self):

        self.env.execute('install', task_retries=0)

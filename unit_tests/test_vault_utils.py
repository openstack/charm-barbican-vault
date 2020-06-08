# Copyright 2018 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import mock

import charm.vault_utils as vault_utils

import charms_openstack.test_utils as test_utils


class TestVaultUtils(test_utils.PatchHelper):

    def test_retrieve_secret_id(self):
        self.patch_object(vault_utils, 'hvac')
        hvac_client = mock.MagicMock()
        self.hvac.Client.return_value = hvac_client
        response = mock.MagicMock()
        response.status_code = 200
        response.json.return_value = {'data': {'secret_id': 'FAKE_SECRET_ID'}}
        hvac_client._post.return_value = response
        self.assertEqual(
            vault_utils.retrieve_secret_id('url', 'token'), 'FAKE_SECRET_ID')
        hvac_client._post.assert_called_with('/v1/sys/wrapping/unwrap')
        self.hvac.Client.assert_called_once_with(
            token='token',
            url='url',
            adapter=self.hvac.adapters.Request,
            verify=vault_utils.SYSTEM_CA_BUNDLE)

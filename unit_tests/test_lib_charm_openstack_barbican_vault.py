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

import charms_openstack.test_utils as test_utils

import charm.openstack.barbican_vault as barbican_vault


class Helper(test_utils.PatchHelper):

    def setUp(self):
        super().setUp()
        self.patch_release(barbican_vault.BarbicanVaultCharm.release)


class TestBarbicanVaultCharm(Helper):

    def test_install_ca_cert(self):
        b = barbican_vault.BarbicanVaultCharm()
        self.patch('charmhelpers.core.host.install_ca_cert', 'install_ca_cert')
        cc = mock.MagicMock()
        b.configuration_class = cc
        b.install_ca_cert('data')
        b.configuration_class.assert_called_once_with()
        self.install_ca_cert.assert_called_once_with(
            'data',
            name=cc().application_name.__radd__())

    def test_secret_backend_name(self):
        b = barbican_vault.BarbicanVaultCharm()
        cc = mock.MagicMock()
        cc().application_name = 'application_name'
        b.configuration_class = cc
        self.assertEqual(b.secret_backend_name, 'charm-application_name')
        cc.assert_has_calls([mock.call(), mock.call()])

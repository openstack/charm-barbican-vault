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

import charms_openstack.adapters
import charms_openstack.charm

import charmhelpers.core as ch_core


class BarbicanVaultCharm(charms_openstack.charm.OpenStackCharm):
    release = 'rocky'
    name = 'barbican-vault'
    packages = ['python3-castellan']
    python_version = 3
    required_relations = ['secrets-storage']
    adapters_class = charms_openstack.adapters.OpenStackRelationAdapters

    _installed_ca_name = None

    def install_ca_cert(self, ca_cert_data):
        """Install CA certificate.

        Takes certificate data from caller and installs it building filename
        from application name in Juju model.

        :param ca_cert_data: Certificate data
        :type ca_cert_data: str
        """
        name = 'juju-' + self.configuration_class().application_name
        ch_core.host.install_ca_cert(ca_cert_data, name=name)
        self._installed_ca_name = (
            '/usr/local/share/ca-certificates/{}.crt'.format(name))

    @property
    def secret_backend_name(self):
        """Build secret backend name from name of the deployed charm."""
        return 'charm-' + self.configuration_class().application_name

    @property
    def installed_ca_name(self):
        """Return installed CA name if set."""
        return self._installed_ca_name

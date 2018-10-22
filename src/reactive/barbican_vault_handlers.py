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
import charmhelpers.core as ch_core

import charms.reactive as reactive

import charms_openstack.bus
import charms_openstack.charm as charm

import charm.vault_utils as vault_utils

charms_openstack.bus.discover()

# Use the charms.openstack defaults for common states and hooks
charm.use_defaults(
    'charm.installed',
    'config.changed',
    'update-status')


@reactive.when_not('secrets-storage.available')
@reactive.when('secrets-storage.connected')
def secret_backend_vault_request():
    """Request access to vault."""
    secrets_storage = reactive.endpoint_from_flag(
        'secrets-storage.connected')
    ch_core.hookenv.log('Requesting access to vault ({})'
                        .format(secrets_storage.vault_url),
                        level=ch_core.hookenv.INFO)
    with charm.provide_charm_instance() as barbican_vault_charm:
        secrets_storage.request_secret_backend(
            barbican_vault_charm.secret_backend_name, isolated=False)
    reactive.clear_flag('secrets-storage.connected')


@reactive.when_all('endpoint.secrets.joined', 'secrets-storage.available',
                   'endpoint.secrets-storage.changed')
def plugin_info_barbican_publish():
    barbican = reactive.endpoint_from_flag('endpoint.secrets.joined')
    secrets_storage = reactive.endpoint_from_flag(
        'secrets-storage.available')
    ch_core.hookenv.log('Retrieving secret-id from vault ({})'
                        .format(secrets_storage.vault_url),
                        level=ch_core.hookenv.INFO)
    secret_id = vault_utils.retrieve_secret_id(
        secrets_storage.vault_url,
        secrets_storage.unit_token)
    with charm.provide_charm_instance() as barbican_vault_charm:
        vault_data = {
            'approle_role_id': secrets_storage.unit_role_id,
            'approle_secret_id': secret_id,
            'vault_url': secrets_storage.vault_url,
            'kv_mountpoint': barbican_vault_charm.secret_backend_name,
            'use_ssl': 'false',  # XXX
        }
        ch_core.hookenv.log('Publishing vault plugin info to barbican',
                            level=ch_core.hookenv.INFO)
        barbican.publish_plugin_info('vault', vault_data)
        reactive.clear_flag('endpoint.secrets-storage.changed')

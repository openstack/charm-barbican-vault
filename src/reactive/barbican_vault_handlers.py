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
import hvac

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
        barbican_vault_charm.assess_status()


def get_secret_id(secrets_storage, current_secret_id=None):
    """Get tokens from relation and try to fetch secret-id from Vault api

    Try all tokens until one succeeds. If all fail, return cached token
    otherwise raise hvac.exceptions.InvalidRequest.
    """
    tokens = secrets_storage.all_unit_tokens
    url = secrets_storage.vault_url
    for i, token in enumerate(tokens):
        try:
            secret_id = vault_utils.retrieve_secret_id(url, token)
            return secret_id
        except hvac.exceptions.InvalidRequest:
            if i == len(tokens) - 1:
                if current_secret_id:
                    return current_secret_id
                else:
                    raise
            else:
                pass


@reactive.when_all('endpoint.secrets.joined', 'secrets-storage.available',
                   'endpoint.secrets-storage.changed')
def plugin_info_barbican_publish():
    barbican = reactive.endpoint_from_flag('endpoint.secrets.joined')
    secrets_storage = reactive.endpoint_from_flag(
        'secrets-storage.available')

    # fetch current secret-id, if any, from relation with barbican principle
    current_secret_id = None
    secrets = reactive.endpoint_from_flag('secrets.available')
    if secrets:
        for relation in secrets.relations:
            data = relation.to_publish.get('data')
            if data and data.get('approle_secret_id'):
                current_secret_id = data.get('approle_secret_id')

    with charm.provide_charm_instance() as barbican_vault_charm:
        if secrets_storage.vault_ca:
            ch_core.hookenv.log('Installing vault CA certificate')
            barbican_vault_charm.install_ca_cert(secrets_storage.vault_ca)
        ch_core.hookenv.log('Retrieving secret-id from vault ({})'
                            .format(secrets_storage.vault_url),
                            level=ch_core.hookenv.INFO)
        secret_id = get_secret_id(secrets_storage, current_secret_id)
        vault_data = {
            'approle_role_id': secrets_storage.unit_role_id,
            'approle_secret_id': secret_id,
            'vault_url': secrets_storage.vault_url,
            'kv_mountpoint': barbican_vault_charm.secret_backend_name,
        }
        if barbican_vault_charm.installed_ca_name:
            vault_data.update({
                'ssl_ca_crt_file': barbican_vault_charm.installed_ca_name})
        ch_core.hookenv.log('Publishing vault plugin info to barbican',
                            level=ch_core.hookenv.INFO)
        barbican.publish_plugin_info('vault', vault_data)
        reactive.clear_flag('endpoint.secrets-storage.changed')
        barbican_vault_charm.assess_status()

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


SYSTEM_CA_BUNDLE = '/etc/ssl/certs/ca-certificates.crt'


# TODO: There is a version in  charmhelpers.contrib.openstack.vaultlocker
# that does everything but the System CA bundle. Update that helper to allow
# a CA bundle for verify.
def retrieve_secret_id(url, token):
    # hvac 0.10.1 changed default adapter to JSONAdapter
    client = hvac.Client(
        url=url, token=token,
        adapter=hvac.adapters.Request,
        verify=SYSTEM_CA_BUNDLE)
    # workaround for issue where callng `client.unwrap(token)` results in
    # "error decrementing wrapping token's use-count: invalid token entry
    #  provided for use count decrementing"
    response = client._post('/v1/sys/wrapping/unwrap')
    if response.status_code == 200:
        data = response.json()
        return data['data']['secret_id']

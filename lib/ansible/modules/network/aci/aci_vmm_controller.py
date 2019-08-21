#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: aci_vmm_controller
short_description: Manage virtual domain controller profiles (vmm:CtrlrP)
description:
- Manage virtual domain controller profiles on Cisco ACI fabrics.
version_added: '2.9'
options:
  name:
    description:
    - Name of the controller profile.
    type: str
    aliases: [ controller_name, controller_profile ]
  container:
    description:
    - Top level container in the controller.
    type: str
    aliases: [ datacenter ]
  credential:
    description:
    - Credential to authenticate with the controller.
    type: str
    aliases: [ credential_name, credential_profile ]
  description:
    description:
    - Description for the tenant.
    type: str
    aliases: [ descr ]
  domain:
    description:
    - Name of the virtual domain profile.
    type: str
    aliases: [ domain_name, domain_profile, name ]
  host_or_ip:
    description:
    - FQDN or IP of the controller.
    type: str
    aliases: [ controller_hostname, controller_ip ]
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
  vm_provider:
    description:
    - The VM platform for VMM Domains.
    - Support for Kubernetes was added in ACI v3.0.
    - Support for CloudFoundry, OpenShift and Red Hat was added in ACI v3.1.
    type: str
    choices: [ cloudfoundry, kubernetes, microsoft, openshift, openstack, redhat, vmware ]
extends_documentation_fragment: aci
seealso:
- module: aci_domain
- name: APIC Management Information Model reference
  description: More information about the internal APIC classes B(vmm:DomP)
  link: https://developer.cisco.com/docs/apic-mim-ref/
author:
- Jason Juenger (@jasonjuenger)
'''

EXAMPLES = r'''
- name: Add credential to VMware VMM domain
  aci_vmm_credential:
    host: apic
    username: admin
    password: SomeSecretPassword
    domain: vmware_dom
    description: secure credential
    name: vCenterCredential
    credential_username: vCenterUsername
    credential_password: vCenterPassword
    vm_provider: vmware
    state: present

- name: Remove credential from VMware VMM domain
  aci_vmm_credential:
    host: apic
    username: admin
    password: SomeSecretPassword
    domain: vmware_dom
    name: myCredential
    vm_provider: vmware
    state: absent

- name: Query a specific VMware VMM credential
  aci_vmm_credential:
    host: apic
    username: admin
    password: SomeSecretPassword
    domain: vmware_dom
    name: vCenterCredential
    vm_provider: vmware
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all VMware VMM credentials
  aci_vmm_credential:
    host: apic
    username: admin
    password: SomeSecretPassword
    domain: vmware_dom
    vm_provider: vmware
    state: query
  delegate_to: localhost
  register: query_result
'''

RETURN = r'''
current:
  description: The existing configuration from the APIC after the module has finished
  returned: success
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production environment",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
error:
  description: The error information as returned from the APIC
  returned: failure
  type: dict
  sample:
    {
        "code": "122",
        "text": "unknown managed object class foo"
    }
raw:
  description: The raw output returned by the APIC REST API (xml or json)
  returned: parse error
  type: str
  sample: '<?xml version="1.0" encoding="UTF-8"?><imdata totalCount="1"><error code="122" text="unknown managed object class foo"/></imdata>'
sent:
  description: The actual/minimal configuration pushed to the APIC
  returned: info
  type: list
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment"
            }
        }
    }
previous:
  description: The original configuration from the APIC before the module has started
  returned: info
  type: list
  sample:
    [
        {
            "fvTenant": {
                "attributes": {
                    "descr": "Production",
                    "dn": "uni/tn-production",
                    "name": "production",
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": ""
                }
            }
        }
    ]
proposed:
  description: The assembled configuration from the user-provided parameters
  returned: info
  type: dict
  sample:
    {
        "fvTenant": {
            "attributes": {
                "descr": "Production environment",
                "name": "production"
            }
        }
    }
filter_string:
  description: The filter string used for the request
  returned: failure or debug
  type: str
  sample: ?rsp-prop-include=config-only
method:
  description: The HTTP method used for the request to the APIC
  returned: failure or debug
  type: str
  sample: POST
response:
  description: The HTTP response from the APIC
  returned: failure or debug
  type: str
  sample: OK (30 bytes)
status:
  description: The HTTP status from the APIC
  returned: failure or debug
  type: int
  sample: 200
url:
  description: The HTTP url used for the request to the APIC
  returned: failure or debug
  type: str
  sample: https://10.11.12.13/api/mo/uni/tn-production.json
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.aci import ACIModule, aci_argument_spec

VM_PROVIDER_MAPPING = dict(
    cloudfoundry='CloudFoundry',
    kubernetes='Kubernetes',
    microsoft='Microsoft',
    openshift='OpenShift',
    openstack='OpenStack',
    redhat='Redhat',
    vmware='VMware',
)


def main():
    argument_spec = aci_argument_spec()
    argument_spec.update(
        name=dict(type='str', aliases=['credential_name', 'credential_profile']),
        container=dict(type='str', aliases=['datacenter']),
        credential=dict(type='str', aliases=['credential_name, credential_profile']),
        description=dict(type='str', aliases=['descr']),
        domain=dict(type='str', aliases=['domain_name', 'domain_profile']),
        host_or_ip=dict(type='str', aliases=['controller_hostname', 'controller_ip']),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
        vm_provider=dict(type='str', choices=VM_PROVIDER_MAPPING.keys())
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['domain']],
            ['state', 'present', ['domain']],
        ],
    )

    name = module.params['name']
    container = module.params['container']
    credential = module.params['credential']
    description = module.params['description']
    domain = module.params['domain']
    host_or_ip = module.params['host_or_ip']
    state = module.params['state']
    vm_provider = module.params['vm_provider']

    controller_class = 'vmmCtrlrP'
    ctrlr_mo = 'uni/vmmp-{0}/dom-{1}/ctrlr-{2}'.format(VM_PROVIDER_MAPPING[vm_provider], domain, name)
    ctrlr_rn = 'vmmp-{0}/dom-{1}/ctrlr-{2}'.format(VM_PROVIDER_MAPPING[vm_provider], domain, name)

    # Ensure that querying all objects works when only domain is provided
    if name is None:
        ctrlr_mo = None

    aci = ACIModule(module)
    aci.construct_url(
        root_class=dict(
            aci_class=controller_class,
            aci_rn=ctrlr_rn,
            module_object=ctrlr_mo,
            target_filter={'name': domain, 'ctrlr': name},
        ),
    )

    aci.get_existing()

    if state == 'present':
        aci.payload(
            aci_class=controller_class,
            class_config=dict(
                descr=description,
                hostOrIp=host_or_ip,
                name=name,
                rootContName=container
            ),
            childConfigs=[dict(
                vmmRsAcc=dict(
                    attributes=dict(
                        tDn=credential,
                    ),
                ),
            )],
        )

        aci.get_diff(aci_class=controller_class)

        aci.post_config()

    elif state == 'absent':
        aci.delete_config()

    aci.exit_json()


if __name__ == "__main__":
    main()

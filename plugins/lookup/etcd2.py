# (c) 2013, Jan-Piet Mens <jpmens(at)gmail.com>
# (m) 2017, Juan Manuel Parrilla <jparrill@redhat.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

try:
    import json
except ImportError:
    import simplejson as json

from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url

# this can be made configurable, not should not use ansible.cfg
if os.getenv('ANSIBLE_ETCD_URL') is not None:
    ANSIBLE_ETCD_URL = os.environ['ANSIBLE_ETCD_URL']
else:
    ANSIBLE_ETCD_URL = 'http://127.0.0.1:4001'

class Etcd:
    def __init__(self, url=ANSIBLE_ETCD_URL, validate_certs=True):
        self.url = url
        self.baseurl = '%s/v2/keys' % (self.url)
        self.validate_certs = validate_certs

    def get(self, key):
        url = "%s/%s" % (self.baseurl, key)

        data = None
        value = ""
        try:
            r = open_url(url, validate_certs=self.validate_certs)
            data = r.read()
        except:
            return value

        try:
            item = json.loads(data)
            if 'node' in item:
                item = item['node']
                if 'nodes' in item:
                    var_map = {}
                    for node in item['nodes']:
                        var_map[node['key'].split('/')[-1]] = node['value']

                    return var_map

                elif 'value' in item:
                    value = item['value']

        except:
            raise
            pass

        return value

class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        validate_certs = kwargs.get('validate_certs', True)

        etcd = Etcd(validate_certs=validate_certs)

        ret = []
        for term in terms:
            key = term.split()[0]
            value = etcd.get(key)
            ret.append(value)
        return ret

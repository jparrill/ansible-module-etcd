# ansible-module-etcd
Ansible Module to manage ETCD Keys and Values, also a Lookup plugin

## Requirements
- Ansible >= 2.1
- python-etcd package
- Docker (optional, Just to try the module)

### Fedora
```
sudo dnf install ansible python2-requests python2-python-etcd
```

### Virtualenv
```
sudo dnf install python2-virtualenv
virtualenv -p python2 .virtualenv
source .virtualenv/bin/activate
pip install python-etcd ansible
```

## How to try
### 1. Start a ETCD server
We will work with Docker, execute this commands to start a new etcd server:

```
docker pull quay.io/coreos/etcd:latest
export HostIP='MyIP'
docker run -it --rm -v /usr/share/ca-certificates/:/etc/ssl/certs -p 4001:4001 -p 2380:2380 -p 2379:2379 --name etcd quay.io/coreos/etcd etcd --name etcd0 -advertise-client-urls http://${HostIP}:2379,http://${HostIP}:4001 -listen-client-urls http://0.0.0.0:2379,http://0.0.0.0:4001 -initial-advertise-peer-urls http://${HostIP}:2380 -listen-peer-urls http://0.0.0.0:2380 -initial-cluster-token etcd-cluster-1 -initial-cluster etcd0=http://${HostIP}:2380 -initial-cluster-state new
```

### 2. Prepare the environment & Execution
I will assume that we already have all the requirements fullfiled (docker daemon up and all this stuff)

```
git clone https://github.com/padajuan/ansible-module-etcd.git
cd ansible-module-etcd
ansible-playbook -i inv sample.yml -u <username>
```

**Output**:
```
PLAY [Sampple for ETCD Module] *************************************************

TASK [setup] *******************************************************************
ok: [localhost]

TASK [Set Key-Value on etcd] ***************************************************
changed: [localhost -> localhost]

TASK [Set the same Key-Value on etcd] ******************************************
ok: [localhost -> localhost]

TASK [Search the Key on ETCD] **************************************************
ok: [localhost] => {
    "msg": "The ETCD contains 'etcd_record' value"
}

TASK [Delete Key-Value from ETCD] **********************************************
changed: [localhost -> localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=5    changed=2    unreachable=0    failed=0   
```

## Desired Module way of work
### ETCD Module
This Module are prepared to **NOT** override any value on ETCD, I will implement this feature soon.

### ETCD Lookup
This lookup plugin will connect by default to http://127.0.0.1:4001, you must set some environment variables: 

#### ANSIBLE_ETCD_URL
- ANSIBLE_ETCD_URL=http://127.0.0.1:4001
```
export ANSIBLE_ETCD_URL=http://127.0.0.1:2379
```

This environment variable will change the URL of ETCD that you are pointing to

#### ANSIBLE_ETCD_VERSION
- ANSIBLE_ETCD_VERSION=v2
```sh
export ANSIBLE_ETCD_VERSION=v2
```

This environment variable will change the version of ETCD that you are pointing to

**FEATURE**: This lookup has been modified from th original one to be capable to get all variables from a ETCD folder.

```
PLAY [Openstack Life-Cycle Management Framework] *********************************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************************************************
ok: [localhost]

TASK [Getting Variables from ETCD Folder] ****************************************************************************************************************************************************
ok: [localhost]

TASK [debug] *********************************************************************************************************************************************************************************
ok: [localhost] => {
    "changed": false,
    "msg": {
        ...
        ...
        ...
        "CEILOMETER_API_PORT": "8777",
        "CEILOMETER_LOG": "LOG_LOCAL6",
        "CEILOMETER_TTL": "7776000",
        "CEILOMETER_USER": "ceilometer",
        "CEPH_VERSION": "0.80.8",
        "CINDER_BCK_DRIVER": "cinder.backup.drivers.ceph",
        "CINDER_CEPH_BCK_USER": "backup",
        "CINDER_CEPH_CHUNK": "134217728",
        "CINDER_DB": "cinder",
        "CINDER_DEF_VOL": "standard",
        "CINDER_ENABLE_BACKEND": "standard,ssd",
        ...
        ...
      }
}

TASK [00_entry_validation : Creating controller files] ***************************************************************************************************************************************
changed: [localhost] => (item={'key': u'ceilometer', 'value': {u'origin': u'/etc/ceilometer/ceilometer.conf', u'tmp': u'/home/test/ceilometer.conf', u'template': u'ceilometer-controller.conf.j2'}})

PLAY RECAP ***********************************************************************************************************************************************************************************
localhost                  : ok=4    changed=1    unreachable=0    failed=0   
```

## Testing
To execute all test, just execute the playbook on test folder, to perform all the E2E tests (Lookup included). From base folder, execute this:

```
ansible-playbook -i inv tests/etcd.yml -u <username>
```

**output**:
```
PLAY [Testing ETCD Module] *****************************************************

TASK [setup] *******************************************************************
ok: [localhost]

TASK [[TEST][MUST CHANGE] Set Value on etcd] ***********************************
changed: [localhost -> localhost] => (item={u'value': u'test_value', u'key': u'/test_key'})
changed: [localhost -> localhost] => (item={u'value': u'test_inner_value', u'key': u'/test/test_inner_key'})

TASK [[TEST][MUST OK] Set the same value on etcd] ******************************
ok: [localhost -> localhost] => (item={u'value': u'test_value', u'key': u'/test_key'})
ok: [localhost -> localhost] => (item={u'value': u'test_inner_value', u'key': u'/test/test_inner_key'})

TASK [[TEST][MUST FAIL] Try to override the value on etcd] *********************
failed: [localhost -> localhost] (item={u'value': u'test_value_OVERRIDE', u'key': u'/test_key'}) => {"failed": true, "item": {"key": "/test_key", "value": "test_value_OVERRIDE"}, "msg": "The Key '/test_key' is already set with 'test_value', exiting..."}
failed: [localhost -> localhost] (item={u'value': u'test_inner_value_OVERRIDE', u'key': u'/test/test_inner_key'}) => {"failed": true, "item": {"key": "/test/test_inner_key", "value": "test_inner_value_OVERRIDE"}, "msg": "The Key '/test/test_inner_key' is already set with 'test_inner_value', exiting..."}
...ignoring

TASK [set_fact] ****************************************************************
ok: [localhost]

TASK [debug] *******************************************************************
skipping: [localhost] => (item=test_value)
skipping: [localhost] => (item=test_inner_value)
skipping: [localhost] => (item=test_value)
skipping: [localhost] => (item=test_inner_value)

TASK [[TEST LOOKUP] Cheking ETCD Values] ***************************************
skipping: [localhost] => (item={u'val2': u'test_value', u'val1': u'test_value'})
skipping: [localhost] => (item={u'val2': u'test_inner_value', u'val1': u'test_inner_value'})

TASK [[TEST][MUST CHANGE] Delete Value on etcd] ********************************
changed: [localhost -> localhost] => (item=/test_key)
changed: [localhost -> localhost] => (item=/test/test_inner_key)

PLAY RECAP *********************************************************************
localhost                  : ok=6    changed=2    unreachable=0    failed=0   
```

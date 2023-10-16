"""
Testing Jenkins Slave Configurations
"""
import os
import requests
import json
import testinfra
from yaml import load
from yaml import Loader
from requests.auth import HTTPBasicAuth

from testinfra.utils.ansible_runner import AnsibleRunner


testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('master')


def jenkins_ip():
    host = testinfra.\
        get_host("docker://root@ubuntu-focal-jenkins-master", sudo=True)
    jenkins_master_address = host.\
        addr("ubuntu-focal-jenkins-master").ipv4_addresses
    return jenkins_master_address[0]


def molecule_yml():
    molecule_yaml = open(os.environ['MOLECULE_FILE'], 'r')
    return load(molecule_yaml, Loader)


def test_jenkins_number_of_nodes(host):
    nodes = requests.get('http://%s:8080/computer/api/json' %
                         jenkins_ip(),
                         auth=HTTPBasicAuth('admin', 'admin'))
    assert nodes.ok
    computers_rsp = json.loads(nodes.content).get('computer')
    instances = molecule_yml().get('platforms')
    assert computers_rsp.__len__() is instances.__len__()

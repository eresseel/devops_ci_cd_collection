"""
Testing Jenkins Slave
"""
import os

from testinfra.utils import ansible_runner


testinfra_hosts = ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('slave')


def test_jenkins_agent(host):
    user = host.user("jenkins")
    assert "/home/jenkins" == user.home

    assert host.exists("java")

    slave_service = host.service('jenkins-slave')
    assert slave_service.is_running
    assert slave_service.is_enabled

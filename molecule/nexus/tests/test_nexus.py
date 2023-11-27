"""
Testing Nexus Configuration
"""
import os
import json
import requests
import testinfra
from pytest import mark
from requests.auth import HTTPBasicAuth

from testinfra.utils.ansible_runner import AnsibleRunner


testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nexus')
repo_json = None
repo_with_beta_json = None


def get_nexus_repos():
    global repo_json
    if not repo_json:
        repo_json = nexus_get_request('/service/rest/v1/repositories')

    return repo_json


def get_nexus_repos_with_beta():
    global repo_with_beta_json
    if not repo_with_beta_json:
        repo_with_beta_json = \
            nexus_get_request('/service/rest/beta/repositories')

    return repo_with_beta_json


def nexus_ip():
    host = testinfra.\
        get_host("docker://root@ubuntu-focal-nexus", sudo=True)
    nexus_address = host.\
        addr("ubuntu-focal-nexus").ipv4_addresses
    return nexus_address[0]


def nexus_get_request(what):
    r = requests.get('http://%s:8081%s' %
                     (nexus_ip(), what),
                     auth=HTTPBasicAuth(username='admin',
                                        password='admin123'))
    return r


def test_admin_credential_setup():
    r = nexus_get_request("/service/rest/v1/script")

    assert r.status_code == 200


def test_blob_store_created():
    r = nexus_get_request("/service/rest/v1/blobstores/test/quota-status")

    assert r.status_code == 200


def expected_repo(repo_name, repo_format, repo_type="hosted"):
    repo_url = 'http://%s:8081/repository/%s' % (nexus_ip(), repo_name)
    repo_attribute = {}
    expected_repo = {
            u'url': repo_url,
            u'attributes': repo_attribute,
            u'type': repo_type,
            u'format': repo_format,
            u'name': repo_name
            }

    return expected_repo


def find_group_repository_with_beta(repositories, repo_name):
    for repo in repositories:
        if repo[u'name'] is not None and repo[u'name'] == repo_name:
            return repo

    return None


def is_expected_repo_exist(
     repositories, repo_name, repo_format, repo_list, repo_type):
    expected_repo = None

    for repo in repositories:
        if repo[u'name'] is not None and repo[u'name'] == repo_name:
            expected_repo = repo

    if expected_repo[u'format'] is not None and \
       expected_repo[u'format'] == repo_format and \
       expected_repo[u'group'][u'memberNames'] is not None and \
       expected_repo[u'group'][u'memberNames'] == repo_list and \
       expected_repo[u'type'] is not None and \
       expected_repo[u'type'] == repo_type:
        is_group = True
    else:
        is_group = False

    return is_group


def is_expected_cleanup_policy_assign_exist(
     repositories, repo_name, repo_format, cleanup_policy_name, repo_type):
    expected_repo = None

    for repo in repositories:
        if repo[u'name'] is not None and repo[u'name'] == repo_name:
            expected_repo = repo

    if expected_repo[u'format'] is not None and \
       expected_repo[u'format'] == repo_format and \
       expected_repo[u'cleanup'] is not None and \
       expected_repo[u'cleanup']['policyNames'] is not None and \
       expected_repo[u'cleanup']['policyNames'] == cleanup_policy_name and \
       expected_repo[u'type'] is not None and \
       expected_repo[u'type'] == repo_type:
        is_cleanup_policy = True
    else:
        is_cleanup_policy = False

    return is_cleanup_policy


def test_helm_repo_exists():
    r = get_nexus_repos()

    repositories = json.loads(r.content)

    assert r.status_code == 200
    assert expected_repo(u'boat', u'helm') in repositories


@mark.parametrize("repo_name,repo_format,repo_type", [
        (u'slytherin', u'pypi', u'hosted')
        ])
def test_pypi_repo_exists(repo_name, repo_format, repo_type):
    r = get_nexus_repos()

    repositories = json.loads(r.content)
    assert r.status_code == 200
    assert expected_repo(repo_name, repo_format, repo_type) in repositories


@mark.parametrize("repo_name,repo_format,repo_type", [
        (u'noodle', u'npm', u'hosted')
        ])
def test_npm_repo_exists(repo_name, repo_format, repo_type):
    r = get_nexus_repos()

    repositories = json.loads(r.content)
    assert r.status_code == 200
    assert expected_repo(repo_name, repo_format, repo_type) in repositories


@mark.parametrize("repo_name,repo_format,repo_type", [
        (u'barbarian', u'conan', u'hosted'),
        ])
def test_conan_repos_exist(repo_name, repo_format, repo_type):
    r = get_nexus_repos()

    repositories = json.loads(r.content)
    assert r.status_code == 200
    assert expected_repo(repo_name, repo_format, repo_type) in repositories


@mark.parametrize("repo_name,repo_format,repo_type", [
    ("maven-central", "maven2", "proxy"),
    ("maven-public", "maven2", "proxy"),
    ("maven-releases", "maven2", "hosted"),
    ("maven-snapshots", "maven2", "hosted"),
    ("nuget-group", "nuget", "group"),
    ("nuget-hosted", "nuget", "hosted"),
    ("nuget.org-proxy", "nuget", "proxy")
    ])
def test_default_repos_dont_exist(repo_name, repo_format, repo_type):
    r = get_nexus_repos()
    repositories = json.loads(r.content)

    assert r.status_code == 200
    assert expected_repo(repo_name, repo_format, repo_type) not in repositories


@mark.parametrize("repo_name,repo_format,repo_type", [
        (u'npm-public', u'npm', u'group'),
        (u'noodle', u'npm', u'hosted'),
        (u'foo', u'npm', u'hosted')
        ])
def test_npm_group_and_npm_repos_exists(repo_name, repo_format, repo_type):
    r = get_nexus_repos()

    repositories = json.loads(r.content)
    assert r.status_code == 200
    assert expected_repo(repo_name, repo_format, repo_type) in repositories


@mark.parametrize("repo_name,repo_format,repo_list,repo_type", [
        (u'npm-public', u'npm', [u'noodle', u'foo'], u'group')
        ])
def test_npm_group_and_members_exists(
     repo_name, repo_format, repo_list, repo_type):
    r = get_nexus_repos_with_beta()

    repositories = json.loads(r.content)
    assert r.status_code == 200
    attribute = is_expected_repo_exist(
        repositories,
        repo_name,
        repo_format,
        repo_list,
        repo_type
    )
    assert attribute is True


@mark.parametrize("repo_name,repo_format,cleanup_policy_name,repo_type", [
        (u'docker-foobar', u'docker', [u'remove-docker-test'], u'hosted'),
        (u'boat', u'helm', [u'remove-helm-test'], u'hosted'),
        (u'maven-foobar', u'maven2', [u'remove-maven-test'], u'hosted'),
        (u'foo', u'npm', [u'remove-npm-test'], u'hosted'),
        (u'slytherin', u'pypi', [u'remove-pypi-test'], u'hosted'),
        (u'raw-foobar', u'raw', [u'remove-raw-test'], u'hosted')
        ])
def test_cleanup_policies_exists(
     repo_name, repo_format, cleanup_policy_name, repo_type):
    r = get_nexus_repos_with_beta()

    repositories = json.loads(r.content)
    assert r.status_code == 200
    attribute = is_expected_cleanup_policy_assign_exist(
        repositories,
        repo_name,
        repo_format,
        cleanup_policy_name,
        repo_type
    )
    assert attribute is True


@mark.parametrize("repo_name,repo_format,cleanup_policy_name,repo_type", [
        (u'raw-not-cleanup-policy', u'raw', [u'remove-raw-test'], u'hosted')
        ])
def test_cleanup_policies_not_exists(
     repo_name, repo_format, cleanup_policy_name, repo_type):
    r = get_nexus_repos_with_beta()

    repositories = json.loads(r.content)
    assert r.status_code == 200
    attribute = is_expected_cleanup_policy_assign_exist(
        repositories,
        repo_name,
        repo_format,
        cleanup_policy_name,
        repo_type
    )
    assert attribute is False

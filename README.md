# 1. devops_ci_cd_collection

## 2. Prepare developer environment
```bash
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r test-requirements.txt

molecule test (--all|-s <scenario name>)        // mind that there is no scenario named 'default'
```

## 3. Suported plugins
* authorize-project
* blueocean
* cloudbees-bitbucket-branch-source
* cloudbees-folder
* config-file-provider
* git
* github-branch-source
* gitlab-branch-source
* job-dsl
* kubernetes
* ldap
* matrix-auth
* role-strategy
* sonar
* thinBackup
* workflow-aggregator
* ws-cleanup

## 4. Documentation
* [ansible_role_jenkins_master](roles/ansible_role_jenkins_master/README.md)
* [ansible_role_jenkins_slave](roles/ansible_role_jenkins_slave/README.md)

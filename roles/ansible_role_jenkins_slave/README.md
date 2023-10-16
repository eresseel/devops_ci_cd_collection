# 1. Jenkins JNLP Slave
Configure managed JNLP Slaves in Jenkins

## 2. Requirements
Currently it requires linux slaves which are Ansible managed (the slaves
register themselves in Jenkins).

It is also required that a Jenkins master is up and running, and corresponding
credentials are passed as parameters.

It is also needed that a Jenkins jnlp slave compatible JRE is already installed
and available in the PATH.

## 3. Role Variables
A description of the settable variables for this role should go here, including
any variables that are in defaults/main.yml, vars/main.yml, and any variables
that can/should be set via parameters to the role. Any variables that are read
from other roles and/or the global scope (ie. hostvars, group vars, etc.)
should be mentioned here as well.

### 3.1. Required parameters:
```yml
jenkins_slave_hostname: jenins-master.acme.com # fqdn or ip address
```

### 3.2. Optional parameters:
```yml
jenkins_slave_http_port: 80
jenkins_slave_url_prefix: ""
jenkins_slave_master_url: "http://{{ jenkins_slave_hostname }}:{{ jenkins_slave_http_port }}{{ jenkins_slave_url_prefix }}"
jenkins_slave_admin_username: "admin"
jenkins_slave_admin_password: "admin"
jenkins_slave_workspace: "/home/{{ jenkins_slave_user }}/workspace"
```

## 4. Dependencies
- Already configured Jenkins master
- Already installed Java

## 5. Example Playbook
Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:
```yml
- name: Install Java
  hosts: master, slaves
  roles:
    - role: neilus.oracle-jdk

- name: Setup Jenkins Master
  hosts: master
  roles:
    - role: eresseel.jenkins

- name: Configure Jenkins Slaves
  hosts: slaves
  roles:
    - role: eresseel.jenkins-jnlp-slave
      jenkins_slave_hostname: "{{ hostvar['jenkins-master'].ansible_fqdn }}"
```

## 6. Contributing
We use molecule and tox for testing, therefore for new features you should also
create a corresponding Goss or testinfra test, which could be run with molecule.

Before opening a pull request make sure you issue `tox` and all tests pass.

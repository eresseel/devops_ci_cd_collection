## 1. Ansible Jenkins role
Install and configure Jenkins CI system on Ubuntu systems.

## 2. Requirements
You need Python an GNU tar installed on the target system and sudo privileges.
The role will set up jenkins and the JDKs usnig apt, maven by unarchiving a tarball to /opt.

## 3. Role Variables
A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

### 3.1. defaults/main.yml
```yml
jenkins_master_hostname: "localhost"
jenkins_master_home: '/home/jenkins'
jenkins_master_admin_username: 'admin'
jenkins_master_admin_password: 'admin'
jenkins_master_url_prefix: ''
jenkins_master_http_port: 8080
jenkins_master_retries: 60
jenkins_master_delay: 30
jenkins_master_timeout: 360

jenkins_master_plugins: []
jenkins_master_ssh_credentials: []
jenkins_master_usr_pw_credentials: []
jenkins_master_secret_text_credentials: []
jenkins_master_secret_file_credentials: []
jenkins_master_global_maven_configs: []
jenkins_master_global_properties_environment_variables: []
jenkins_master_global_xml_configs: []
jenkins_master_global_json_configs: []
jenkins_master_oracle_jdk_installations: []
jenkins_master_maven_installations: []
jenkins_master_sonar_servers: []
jenkins_master_bitbucket_endpoint: []
jenkins_master_bitbucket_organization_folders: []
jenkins_master_global_shared_libraries: []
jenkins_master_backup_configuration: []
jenkins_master_smtp_server: ''
jenkins_master_hostname: 'localhost'
jenkins_master_admin_address: 'jenkins@localhost'
jenkins_master_access_control_for_builds: []
jenkins_master_executors: 2
jenkins_master_description: "Jenkins main"
jenkins_master_labels: "master,devops"
jenkins_master_usage: 'NORMAL'  # other value: EXCLUSIVE
jenkins_master_use_ldap: false
jenkins_master_ldap: {}
jenkins_master_matrix_authorization_strategy:
  - user_or_group: 'admin'
    permissions:
      - 'hudson.model.Hudson.Administer'
```

## 3.2. playbook configuration
```yml
jenkins_master_hostname: "jenkins.vagrant.com"
jenkins_master_home: '/home/jenkins'
jenkins_master_admin_username: 'admin'
jenkins_master_admin_password: 'admin'
jenkins_master_url_prefix: ''
jenkins_master_http_port: 8080
jenkins_master_retries: 60
jenkins_master_delay: 30
jenkins_master_timeout: 360

jenkins_master_plugins:
  - name: 'ace-editor'
    version: '1.1'
  - name: 'apache-httpcomponents-client-4-api'
    version: '4.5.13-138.v4e7d9a_7b_a_e61'
jenkins_master_ssh_credentials:
  - id: sjenkins
    username: sjenkins
    content_key_pub: |
      ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDEwMc0aDED9PHkFQnLHzKQTuvgiDI3lkBbwkhOo+crsILlu7hryjIJcG9makzGLd6oWvt2P+2NteTZryQFBHvtYWIeOVNIXb391CDWOaNzg1MDTh60Ef98H8ZSIcn2tHoE6cfkknVgUMs2hjV4bjUwUgBPnFpn4fDfR3OuI4CQa5thUwN1S2UOsZoZNtpZcF0PLzrvyBXL7eGOG4/Ouhk9sdNObt5G4A084js8ctiyG/BdFFvIG/ax0bKFSL27vNcUj+i7zBedzlTdU0AF3Kt1bzt1gpFjj6i6wGWcwswqwa+LsWklgYUotlmTEGLCRyQx7lfusAkSwfBC9CuY2AHzpTtHqag0OOw+kaMjevI8hd8yA5/exEPFOUk2Sv6uI844t9TYeHSSgJx3M92uKVd1TVYjRcIObw0RdWy18ga7iFnMy90e9Bo4RYcS0V1OrFRGto39SHaRu0+JkUlT5RbImo7jBwjTE+F1Yd60e1kvhFqAMMDWQigCq3HBGoZD2RC8HKjicTSWbGMZWdsnQf1seTE3mhyk7DZswDQ7oDS8oBHupl8s8bbsTW0OYid54CSF5OFOpLeK4TgxGtivsqPaQiqguk++430gVBaz0kmGdqqF68LXV2UXQ6cTh2l6au9hLwAl9ws7NMNwZLiNeOEa09r9qarU2y+l59NAHAML3Q== test.services.jenkins@mydomain.com
    content_key: |
      -----BEGIN RSA PRIVATE KEY-----
      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
      -----END RSA PRIVATE KEY-----
jenkins_master_usr_pw_credentials:
  - id: usr_pw_id
    username: foo
    password: bar
    description: "usr_pw_description"
jenkins_master_secret_text_credentials:
  - id: sonar_de_sjenkins_master_auth
    secret: "secret"
    description: 'supersecret'
jenkins_master_secret_file_credentials:
  - id: 'secret_file_id'
    description: 'secret file description'
    file: 'files/secret.file'
jenkins_master_global_maven_configs:
  - id: 'foo-bar-settings-update'
    name: 'foo-bar-settings-update'
    comment: 'Foo Bar maven settings'
    file: 'files/foo-bar-settings-update.xml'
    server_credentials:
      - server_id: 'snapshot'
        credential_id: 'usr_pw_id'
      - server_id: 'release_update'
        credential_id: 'usr_pw_id'
jenkins_master_global_properties_environment_variables:
  - name: 'FOO_BAR_new'
    value: "http://foobar/repository/foobar-release/"
jenkins_master_global_xml_configs:
  - id: 'foo-bar-config-xml-new'
    name: 'foo-bar-config-xml-new'
    comment: 'Foo Bar configuration new'
    file: 'files/foo-bar-settings.xml'
jenkins_master_global_json_configs:
  - id: 'foo-bar-new'
    name: 'foo-bar-new'
    comment: 'Configurations for the NAVSRV pipeline new'
    file: 'files/foo-bar-settings.json'
jenkins_master_oracle_jdk_installations:
  - version: 6-new
    default: true
jenkins_master_maven_installations:
  - name: 'MVN3_new'
    version: '3.3.9'
jenkins_master_sonar_servers:
  - name: 'sonar.devops.dev.mydomain.com'
    server_url: "https://sonar.vagrant.devops.dev.mydomain.com"
    credential_id: sonar_sjenkins_master_auth
jenkins_master_bitbucket_endpoint:
  - display_name: "foo-no-change"
    server_url: "http://foobar.com:7990"
    call_can_merge: true
    call_changes: true
    manage_hooks: true
    credentials_id: "usr_pw_id"
    webhook_implementation: 'PLUGIN'  # NATIVE
jenkins_master_bitbucket_organization_folders:
  - name: 'ORG-FOLD-update'
    display_name: 'ORG-FOLD-update'
    bitbucket_url: "{{ bitbucket_url }}"
    project_key: 'ORG-FOLD'
    scan_credentials: 'bitbucket_admin'
    checkout_credentials: 'sjenkins'
    bitbucket_ssh_port: 7999
    bitbucket_server_name: 'foo'
    project_based_security:
      - user_or_group: 'admin'
        permissions:
          - 'hudson.model.Hudson.Administer'
      - user_or_group: 'bela'
        permissions:
          - 'hudson.model.Hudson.Read'
          - 'hudson.model.Item.Read'
          - 'hudson.model.View.Read'
      - user_or_group: 'karcsi'
        permissions:
          - 'hudson.model.Hudson.Read'
          - 'hudson.model.Item.Read'
    pipeline_libraries:
      - name: 'korte-pipeline-library'
        git_url: "{{ pipeline_git_baseurl }}/korte-pipeline-library.git"
        credentials: 'sjenkins'
        default_version: 'develop'
        implicit: true
jenkins_master_global_shared_libraries:
  - name: 'new-pipeline-library'
    git_url: "{{ pipeline_git_baseurl }}/new-pipeline-library.git"
    credentials: 'sjenkins'
    default_version: 'master'
jenkins_master_backup_configuration:
  - name: "backup config"
    path: "/home/jenkins/jenkins_master_backup_new_path"
    cron: "0 0 * * 5"
    max_backup_nuber: 4
    timeout: 120
    backup_result: true
    backup_next_build_number: true
    move_old_backup_to_zip: true
jenkins_master_smtp_server: ''
jenkins_master_hostname: 'localhost'
jenkins_master_admin_address: 'jenkins@localhost'
jenkins_master_access_control_for_builds:
  - authenticator_type: 'GlobalQueueItemAuthenticator'
    strategy: 'SystemAuthorizationStrategy'
jenkins_master_executors: 2
jenkins_master_description: "Jenkins main"
jenkins_master_labels: "master,devops"
jenkins_master_usage: 'NORMAL'  # other value: EXCLUSIVE
jenkins_master_use_ldap: false
jenkins_master_ldap: {}
jenkins_master_matrix_authorization_strategy:
  - user_or_group: 'admin'
    permissions:
      - 'hudson.model.Hudson.Administer'
```
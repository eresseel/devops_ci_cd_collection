# 1. Nexus
Setup Nexus OSS repository manager.

## 2. Requirements
None.

## 3. Role Variables
```yml
nexus_installation_dir: /home/nexus
nexus_retries: 60
nexus_delay: 30
nexus_timeout: 360
nexus_script_timeout: 60
nexus_port: 8081
nexus_download_url: http://download.sonatype.com/nexus/3
nexus_version: 3.21.2-03
nexus_package: "nexus-{{ nexus_version }}-unix.tar.gz"
nexus_feature_xml: "{{ nexus_installation_dir }}/nexus-{{ nexus_version }}/system/org/sonatype/nexus/assemblies/nexus-core-feature/{{ nexus_version }}/nexus-core-feature-{{ nexus_version }}-features.xml"
nexus_admin_user: "{{ nexus_default_admin_user }}"
nexus_admin_pw: "{{ nexus_default_admin_pw | default('admin123')}}"

nexus_delete_default_repos: true
nexus_ldap_connections: []

#    example ldap config:
#    ldap_name: 'My Company LDAP' # used as a key to update the ldap config
#    ldap_protocol: 'ldaps' # ldap or ldaps
#    ldap_hostname: 'ldap.mycompany.com'
#    ldap_port: 636
#    ldap_search_base: 'dc=mycompany,dc=net'
#    ldap_user_base_dn: 'ou=users'
#    ldap_user_object_class: 'inetOrgPerson'
#    ldap_user_id_attribute: 'uid'
#    ldap_user_real_name_attribute: 'cn'
#    ldap_user_email_attribute: 'mail'
#    ldap_group_base_dn: 'ou=groups'
#    ldap_group_object_class: 'posixGroup'
#    ldap_group_id_attribute: 'cn'
#    ldap_group_member_attribute: 'memberUid'
#    ldap_group_member_format: '${username}'

nexus_roles: []

nexus_core_feature: 'http://karaf.apache.org/xmlns/features/v1.6.0'

nexus_user_role_mappings: []

nexus_blob_stores: []

# also see _nexus_repos_maven_defaults below
nexus_repos_maven_proxy:
  - name: central
    remote_url: 'https://repo1.maven.org/maven2/'
    layout_policy: permissive
  - name: jboss
    remote_url: 'https://repository.jboss.org/nexus/content/groups/public-jboss/'

nexus_repos_maven_hosted:
  - name: private-release
    version_policy: release
    write_policy: allow_once

nexus_repos_maven_group:
  - name: public
    member_repos:
      - central
      - jboss

_nexus_repos_maven_defaults:
  blob_store: default  # Note : cannot be updated once the repo has been created
  strict_content_validation: true
  version_policy: release  # release, snapshot or mixed
  layout_policy: strict  # strict or permissive
  write_policy: allow_once  # allow_once or allow
  content_max_age: 1440
  metadata_max_age: 1440
  time_to_live: 1440

# Docker support
nexus_repos_docker_hosted:
  - name: docker-hosted
    http_port: 9080
    v1_enabled: True

_nexus_repos_docker_defaults:
  blob_store: default  # Note : cannot be updated once the repo has been created
  strict_content_validation: true
  write_policy: allow_once  # allow_once or allow

nexus_repos_raw_hosted:
  - name: raw-internal
    version_policy: release
    write_policy: allow_once

_nexus_repos_raw_defaults:
  blob_store: default  # Note : cannot be updated once the repo has been created
  strict_content_validation: true
  version_policy: release  # release, snapshot or mixed
  layout_policy: strict  # strict or permissive
  write_policy: allow_once  # allow_once or allow

# pypi support ...
_nexus_repos_pypi_defaults:
  blob_store: default
  strict_content_validation: true
  version_policy: release  # release, snapshot or mixed
  layout_policy: strict  # strict or permissive
  write_policy: allow_once  # one of "allow", "allow_once" or "deny"
  maximum_component_age: 1440  # Nexus gui default. For proxies only
  maximum_metadata_age: 1440  # Nexus gui default. For proxies only
  negative_cache_enabled: true  # Nexus gui default. For proxies only
  negative_cache_ttl: 1440  # Nexus gui default. For proxies only

nexus_repos_pypi_hosted:
  - name: pypi-internal
    version_policy: release
    write_policy: allow  # one of "allow", "allow_once" or "deny"

nexus_repos_pypi_group: []
#  - name: pypi-all
#    member_repos:
#      - pypi-internal
#      - pypi

nexus_repos_pypi_proxy: []
#  - name: 'pypi'
#    remote_url: 'https://pypi.python.org/'
#    # maximum_component_age: 1440
#    # maximum_metadata_age: 1440
#    # negative_cache_enabled: true
#    # negative_cache_ttl: 1440

_nexus_repos_npm_defaults:
  blob_store: default
  strict_content_validation: true
  write_policy: allow_once  # one of "allow", "allow_once" or "deny"
  maximum_component_age: 1440  # Nexus gui default. For proxies only
  maximum_metadata_age: 1440  # Nexus gui default. For proxies only
  negative_cache_enabled: true  # Nexus gui default. For proxies only
  negative_cache_ttl: 1440  # Nexus gui default. For proxies only

nexus_repos_npm_hosted:
  - name: npm-internal
    blob_store: default

nexus_repos_npm_group: []

nexus_repos_npm_proxy: []
#  - name: npm-proxy
#    blob_store: default
#    remote_url: 'https://registry.npmjs.org'
#    # maximum_component_age: 1440
#    # maximum_metadata_age: 1440
#    # negative_cache_enabled: true
#    # negative_cache_ttl: 1440

_nexus_repos_helm_defaults:
  blob_store: default  # Note : cannot be updated once the repo has been created
  strict_content_validation: true
  write_policy: allow_once  # allow_once or allow

nexus_repos_helm_hosted: []

_nexus_repos_conan_defaults:
  blob_store: default  # Note : cannot be updated once the repo has been created
  strict_content_validation: true
  write_policy: allow_once  # allow_once or allow

nexus_repos_conan_hosted: []
nexus_repos_conan_proxy:
  - name: 'conan-center'
    remote_url: 'https://bintray.com/conan/conan-center'
  - name: 'bincrafters'
    remote_url: 'https://bintray.com/bincrafters/public-conan'
  - name: 'conan-community'
    remote_url: 'https://bintray.com/conan-community/conan'
nexus_scheduled_tasks: []

#    - name: db-backup # Note: CRON must be aligned to nexus-blob-backup.sh cron schedule. -> Task: "Config nexus-backup shell cron"
#    cron: '0 0 21 * * ?'
#    typeId: db.backup
#    taskProperties:
#    location: "{{ nexus_backup_dir }}/"

nexus_maven_snapshots_cleanup_tasks: []

nexus_repos_cleanup_policies: []
# - name: mvn_cleanup
#   format: maven2
#   mode:
#   notes: ""
#   criteria:
#     lastBlobUpdated: 60  # Optional
#     lastDownloaded: 120  # Optional
#     preRelease: RELEASES # Optional: PRERELEASES or RELEASES
#     regexKey: "foo.*"    # Optional

# - repository: "devops-m2-snapshot" # Maven repository or repository group to remove snapshots from.
#   cron: "0 0 1 1/1 * ? *" # A cron expression that will control the running of the task.
#   minimum_retained: "5" # Minimum number of snapshots to keep for one GAV.
#   snapshots_retention_days: "30" # Purge all snapshots older than this, provided we still keep the minimum number specified.
#   remove_if_released: "true" # Purge all snapshots that have a corresponding release
#   grace_period_in_days: "90" # The grace period during which snapshots with an associated release will not be purged.

plugins_path: "{{ nexus_installation_dir }}/nexus-{{ nexus_version }}/system/org/sonatype/nexus/plugins"
```

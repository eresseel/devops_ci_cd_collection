# """
# Testing Jenkins Master
# """
import os
import testinfra
import time
import jenkins
from jenkins import Jenkins
from testinfra.utils.ansible_runner import AnsibleRunner


testinfra_hosts = AnsibleRunner(
  os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('master')


def jenkins_ip():
    host = testinfra.\
      get_host("docker://root@ubuntu-focal-jenkins-master", sudo=True)
    jenkins_address = host.addr("ubuntu-focal-jenkins-master").ipv4_addresses
    return jenkins_address[0]


def jenkins_server():
    server = Jenkins("http://%s:8080" %
                     jenkins_ip(),
                     username='admin',
                     password='admin',
                     timeout=10)
    return server


def execute_and_wait_for_script_result(groovy_script):
    retry = 40
    running = False
    result = None
    while not running and retry > 0:
        try:
            result = jenkins_server().run_script(groovy_script)
            running = 'Result' in result
        except jenkins.JenkinsException as e:
            result = str(e)
            running = True
        except Exception:
            running = False
            time.sleep(1)
            retry -= 1
    return result


def test_jenkins_service(host):
    assert host.exists("java")

    master_service = host.service('jenkins')
    assert master_service.is_running
    assert master_service.is_enabled


def test_sonar_pugin():
    groovy_script = """
    import jenkins.model.*
    import hudson.plugins.sonar.*
    import hudson.plugins.sonar.model.*
    import hudson.util.Secret

    def inst = Jenkins.getInstance()
    def desc = inst.getDescriptor\
    ("hudson.plugins.sonar.SonarGlobalConfiguration")
    def sonarNamesList = [\
     "sonar.devops.dev.mydomain.com",\
     "sonar.platform.dev.mydomain.com",\
     "sonar.dev.platform.dev.mydomain.com"
    ]
    def sonarUrlsList = [
        "https://sonar.vagrant.devops.dev.mydomain.com",\
        "https://proba.com",\
        "https://proba1.com",\
    ]
    def sonarCredentialsIdsList = [\
        "sonar_sjenkins_master_auth",\
        "sonar_de_sjenkins_master_auth",\
        "sonar_de_sjenkins_master_auth1"
    ]
    def existInsts = desc.getInstallations()
    def existSonarNamesList = []
    def existSonarUrlsList = []
    def existSonarCredentialsIdsList = []
    existInsts.each{
        assert it.name in sonarNamesList
        assert it.serverUrl in sonarUrlsList
        assert it.credentialsId in sonarCredentialsIdsList
    }
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_queue_item_authenticator():
    groovy_script = """
    import jenkins.security.QueueItemAuthenticatorConfiguration
    import org.jenkinsci.plugins.authorizeproject.GlobalQueueItemAuthenticator
    import org.jenkinsci.plugins.authorizeproject.strategy.\
    TriggeringUsersAuthorizationStrategy

    def result = false
    def authenticators = QueueItemAuthenticatorConfiguration.\
      get().getAuthenticators()
    def strategies = authenticators.collect { it.strategy }

    if (strategies.find { TriggeringUsersAuthorizationStrategy.\
      isInstance(it) }) {
      result = true
    }

    return result
    """
    retry = 20
    running = False
    while not running and retry > 0:
        try:
            result = jenkins_server().run_script(groovy_script)
            running = 'Result' in result
        except jenkins.JenkinsException as e:
            result = str(e)
            running = True
        except Exception:
            running = False
            time.sleep(1)
            retry -= 1
    assert result == 'Result: true\n'


def test_global_secret_file_credentials():
    groovy_script = """
    def creds = com.cloudbees.plugins.credentials.CredentialsProvider.\
    lookupCredentials(
      org.jenkinsci.plugins.plaincredentials.FileCredentials.class,
      jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{ cred -> cred.id == 'secret_file_id' }

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).description == 'secret file description'
    assert matchedCreds.get(0).fileName == 'secret_file_id'
    assert matchedCreds.get(0).content.text == 'very secret file'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_secret_text_credentials():
    groovy_script = """
    import hudson.util.Secret
    def creds = com.cloudbees.plugins.credentials.CredentialsProvider.\
    lookupCredentials(
      org.jenkinsci.plugins.plaincredentials.StringCredentials.class,
      jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{ cred -> cred.id == 'secret_text_id' }

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).description == 'secret text description'
    assert Secret.toString(matchedCreds.get(0).secret) == 'secret_text_token'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_usr_pw_credentials():
    groovy_script = """
    import hudson.util.Secret
    def creds = com.cloudbees.plugins.credentials.CredentialsProvider.\
    lookupCredentials(
      com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl.class,
      jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{ cred -> cred.id == 'usr_pw_id' }

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).username == 'foo'
    assert Secret.toString(matchedCreds.get(0).password) == 'bar'
    assert matchedCreds.get(0).description == 'usr_pw_description'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_ssh_credentials():
    groovy_script = """
    def creds = com.cloudbees.plugins.credentials.CredentialsProvider.\
    lookupCredentials(
      com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey.class,
      jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{ cred -> cred.id == 'sjenkins' }

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).username == 'sjenkins'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_installed_plugins():
    plugins_from_server = jenkins_server().get_plugins()
    plugins_from_playbook = ['matrix-auth', 'bouncycastle-api',
                             'script-security', 'jdk-tool',
                             'authorize-project', 'command-launcher',
                             'trilead-api', 'plain-credentials',
                             'structs', 'credentials', 'sonar', 'jaxb',
                             'ssh-credentials', 'scm-api']

    for plugin in plugins_from_playbook:
        assert plugin == plugins_from_server[plugin]['shortName']


def test_global_secret_file_credentials_update():
    groovy_script = """
    def creds = com.cloudbees.plugins.credentials.\
    CredentialsProvider.lookupCredentials(
    org.jenkinsci.plugins.plaincredentials.FileCredentials.class,
    jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{ cred -> \
    cred.id == 'secret_file_id_need_to_update' }

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).description == 'secret file description'
    assert matchedCreds.get(0).fileName == 'secret_file_id_need_to_update'
    assert matchedCreds.get(0).content.text == 'very secret file update'

    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_secret_text_credentials_update():
    groovy_script = """
    import hudson.util.Secret
    def creds = com.cloudbees.plugins.credentials.\
    CredentialsProvider.lookupCredentials(
      org.jenkinsci.plugins.plaincredentials.\
      StringCredentials.class,
      jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{ cred -> \
    cred.id == 'secret_text_id_need_to_update' }

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).description\
     == 'secret text description update'
    assert Secret.toString(matchedCreds.get(0).secret)\
     == 'secret_text_token_update'

    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_usr_pw_credentials_update():
    groovy_script = """
    import hudson.util.Secret
    def creds = com.cloudbees.plugins.credentials.\
    CredentialsProvider.lookupCredentials(
      com.cloudbees.plugins.credentials.impl.\
      UsernamePasswordCredentialsImpl.class,
      jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{ cred ->\
     cred.id == 'usr_pw_id_need_to_update' }

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).username == 'fooo'
    assert Secret.toString(matchedCreds.get(0).password) == 'barba'
    assert matchedCreds.get(0).description == 'usr_pw_description_update'

    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_ssh_credentials_update():
    groovy_script = """
    def creds = com.cloudbees.plugins.credentials.\
    CredentialsProvider.lookupCredentials(
      com.cloudbees.jenkins.plugins.sshcredentials.\
      impl.BasicSSHUserPrivateKey.class,
      jenkins.model.Jenkins.instance
    )

    def matchedCreds = creds.findAll{cred -> cred.id == 'sjenkins'}

    assert matchedCreds.size() == 1
    assert matchedCreds.get(0).username == 'sjenkins'
    assert matchedCreds.get(0).privateKey.contains("update")

    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_shared_pipeline_library_add_new_pipeline():
    groovy_script = """
    import jenkins.model.Jenkins
    import jenkins.plugins.git.GitSCMSource
    import jenkins.plugins.git.traits.BranchDiscoveryTrait
    import org.jenkinsci.plugins.workflow.libs.GlobalLibraries
    import org.jenkinsci.plugins.workflow.libs.LibraryConfiguration
    import org.jenkinsci.plugins.workflow.libs.SCMSourceRetriever

    expectedName = 'new-pipeline-library'
    expectedGitUrl = \
    'ssh://git@bitbucket.atlassian.vagrant.dev:7999/devops/new-pipeline-library.git'
    expectedCredID = 'sjenkins'
    expectedDefaultVersion = 'master'
    def globalPipelines = \
    Jenkins.instance.getExtensionList(GlobalLibraries.class)[0]
    existingPipeline = \
    globalPipelines.libraries.find { it.getName() == expectedName}

    assert existingPipeline.getRetriever().getScm().getRemote() \
      == expectedGitUrl
    assert existingPipeline.getRetriever().getScm().getCredentialsId() \
      == expectedCredID
    assert existingPipeline.getDefaultVersion() == expectedDefaultVersion
    assert existingPipeline.isImplicit() == false
    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_shared_pipeline_library_update_existing_pipeline():
    groovy_script = """
    import jenkins.model.Jenkins
    import jenkins.plugins.git.GitSCMSource
    import jenkins.plugins.git.traits.BranchDiscoveryTrait
    import org.jenkinsci.plugins.workflow.libs.GlobalLibraries
    import org.jenkinsci.plugins.workflow.libs.LibraryConfiguration
    import org.jenkinsci.plugins.workflow.libs.SCMSourceRetriever

    expectedName = \
    'updated-pipeline-library'
    expectedGitUrl = \
    'ssh://git@bitbucket.atlassian.vagrant.dev:7999/devops/updated-pipeline-library.git'
    expectedCredID = 'sjenkins'
    expectedDefaultVersion = 'master'
    def globalPipelines = \
    Jenkins.instance.getExtensionList(GlobalLibraries.class)[0]
    existingPipeline = \
    globalPipelines.libraries.find { it.getName() == expectedName}

    assert existingPipeline.getRetriever().getScm().getRemote() \
      == expectedGitUrl
    assert existingPipeline.getRetriever().getScm().getCredentialsId() \
      == expectedCredID
    assert existingPipeline.getDefaultVersion() == expectedDefaultVersion
    assert existingPipeline.isImplicit() == false
    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_shared_pipeline_library_no_change():
    groovy_script = """
    import jenkins.model.Jenkins
    import jenkins.plugins.git.GitSCMSource
    import jenkins.plugins.git.traits.BranchDiscoveryTrait
    import org.jenkinsci.plugins.workflow.libs.GlobalLibraries
    import org.jenkinsci.plugins.workflow.libs.LibraryConfiguration
    import org.jenkinsci.plugins.workflow.libs.SCMSourceRetriever

    expectedName = 'no-change-pipeline-library'
    expectedGitUrl = \
    'ssh://git@bitbucket.atlassian.vagrant.dev:7999/devops/no-change-pipeline-library.git'
    expectedCredID = 'sjenkins'
    expectedDefaultVersion = 'no-change'
    def globalPipelines = \
    Jenkins.instance.getExtensionList(GlobalLibraries.class)[0]
    existingPipeline = \
    globalPipelines.libraries.find { it.getName() == expectedName}

    assert existingPipeline.getRetriever().getScm().getRemote() \
      == expectedGitUrl
    assert existingPipeline.getRetriever().getScm().getCredentialsId() \
      == expectedCredID
    assert existingPipeline.getDefaultVersion() == expectedDefaultVersion
    assert existingPipeline.isImplicit() == false
    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_location_configuration_no_change():
    groovy_script = """
    def jlc = JenkinsLocationConfiguration.get()

    assert jlc.getUrl() == "https://ubuntu-focal-jenkins-master/"
    assert jlc.getAdminAddress() == "foo@bar.com"
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_json_config_file_provider_new():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.json.JsonConfig

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-new').name\
       == 'foo-bar-new'
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_xml_config_file_provider_new():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.xml.XmlConfig

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-config-xml-new').name\
       == 'foo-bar-config-xml-new'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_maven_config_file_provider_new():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.maven.MavenSettingsConfig
    import org.jenkinsci.plugins.configfiles.maven.security.\
    ServerCredentialMapping

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-settings-new').name\
       == 'foo-bar-settings-new'
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_mailer_no_change():
    groovy_script = """
    def desc = Jenkins.getInstance().\
      getDescriptor("hudson.tasks.Mailer")
    def smtpHost = "{{ mydomain_jenkins_smtp_host }}"

    assert desc.getSmtpHost() == "foo-bar-update.com"
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_maven_installations_new():
    groovy_script = """
    def maven = Jenkins.instance.\
      getExtensionList(hudson.tasks.Maven.DescriptorImpl.class)[0]

    assert maven.installations.size() == 3
    assert maven.installations.find() {
      it.name == "MVN3_new"
      it.home == "/opt/apache-maven-3.3.9"
    }
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_oracle_jdk_versions_new():
    groovy_script = """
    import hudson.model.JDK.DescriptorImpl

    JDK.DescriptorImpl descriptor = ExtensionList.\
      lookupSingleton(JDK.DescriptorImpl.class)

    def desc = new hudson.model.JDK.DescriptorImpl()
    def jdks = []
    jdks = desc.getInstallations()

    assert jdks.size() == 3
    assert descriptor.getInstallations().toString().\
      contains('JDK[JDK6-new]')
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_properties_environment_new():
    groovy_script = """
    instance = Jenkins.getInstance()
    globalNodeProperties = instance.getGlobalNodeProperties()
    envVarsNodePropertyList = globalNodeProperties.\
      getAll(hudson.slaves.EnvironmentVariablesNodeProperty.class)

    assert envVarsNodePropertyList.get(0).getEnvVars().size()== 3
    assert envVarsNodePropertyList.get(0).getEnvVars().get('FOO_BAR_new') \
      == 'http://foobar/repository/foobar-release/'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_organization_folder_config_new():
    groovy_script = """
    def organizationFolderName = 'TEST-new'
    def organizationFolder = Jenkins.getInstance().\
      getItem(organizationFolderName)

    assert organizationFolder.\
      getDisplayName() == organizationFolderName

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_json_config_file_provider_no_change():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.json.JsonConfig

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-no-change').name\
       == 'foo-bar-no-change'
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_xml_config_file_provider_no_change():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.xml.XmlConfig

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-config-xml-no-change').name\
       == 'foo-bar-config-xml-no-change'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_maven_config_file_provider_no_change():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.maven.MavenSettingsConfig
    import org.jenkinsci.plugins.configfiles.maven.security.\
    ServerCredentialMapping

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-settings-no-change').name\
       == 'foo-bar-settings-no-change'
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_maven_installations_no_change():
    groovy_script = """
    def maven = Jenkins.instance.\
      getExtensionList(hudson.tasks.Maven.DescriptorImpl.class)[0]

    assert maven.installations.size() == 3
    assert maven.installations.find() {
      it.name == "MVN3_new"
      it.home == "/opt/apache-maven-3.3.9"
    }
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_oracle_jdk_versions_no_change():
    groovy_script = """
    import hudson.model.JDK.DescriptorImpl

    JDK.DescriptorImpl descriptor = ExtensionList.\
      lookupSingleton(JDK.DescriptorImpl.class)

    def desc = new hudson.model.JDK.DescriptorImpl()
    def jdks = []
    jdks = desc.getInstallations()

    assert jdks.size() == 3
    assert descriptor.getInstallations().toString().\
      contains('JDK[JDK7-no-change]')
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_properties_environment_update():
    groovy_script = """
    instance = Jenkins.getInstance()
    globalNodeProperties = instance.getGlobalNodeProperties()
    envVarsNodePropertyList = globalNodeProperties.\
      getAll(hudson.slaves.EnvironmentVariablesNodeProperty.class)

    assert envVarsNodePropertyList.get(0).getEnvVars().size()== 3
    assert envVarsNodePropertyList.get(0).getEnvVars().get('FOO_BAR_update') \
      == 'http://foobar_update/repository/foobar-release/'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_organization_folder_config_update():
    groovy_script = """
    def organizationFolderName = "ORG-FOLD-update"
    def organizationFolder = Jenkins.getInstance().\
      getItem(organizationFolderName)
    def actualSharedPipeline = organizationFolder.properties.\
    get(org.jenkinsci.plugins.workflow.libs.FolderLibraries)

    assert organizationFolder.\
      getDisplayName() == organizationFolderName
    assert actualSharedPipeline.getLibraries()[0].\
      getDefaultVersion() == "develop"

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_json_config_file_provider_update():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.json.JsonConfig

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-update').name\
       == 'foo-bar-update'
    assert gcf.getById('foo-bar-update').content == '''{
    "foo": "bar-update"
}'''
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_xml_config_file_provider_update():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.xml.XmlConfig

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-config-xml-update').name\
      == 'foo-bar-config-xml-update'
    assert gcf.getById('foo-bar-config-xml-update').\
      content == '''<?xml version="1.0" encoding="UTF-8"?>
<settings>
    <profiles>
        <profile>
            <id>foobar-update</id>
        </profile>
    </profiles>
</settings>'''

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_maven_config_file_provider_update():
    groovy_script = """
    import org.jenkinsci.plugins.configfiles.*
    import org.jenkinsci.plugins.configfiles.maven.MavenSettingsConfig
    import org.jenkinsci.plugins.configfiles.maven.security.\
    ServerCredentialMapping

    gcf = GlobalConfigFiles.get()

    assert gcf.getById('foo-bar-settings-update').name\
       == 'foo-bar-settings-update'
    assert gcf.getById('foo-bar-settings-update').\
      getServerCredentialMappings()[1].serverId == 'release_update'
    assert gcf.getById('foo-bar-settings-update').\
      content == '''<?xml version="1.0" encoding="UTF-8"?>
<settings>
    <profiles>
        <profile>
            <id>foobar-update</id>
        </profile>
    </profiles>
</settings>'''

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_maven_installations_update():
    groovy_script = """
    def maven = Jenkins.instance.\
      getExtensionList(hudson.tasks.Maven.DescriptorImpl.class)[0]

    assert maven.installations.size() == 3
    assert maven.installations.find() {
      it.name == "MVN3_new"
      it.home == "/opt/apache-maven-3.4.9"
    }
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_oracle_jdk_versions_update():
    groovy_script = """
    import hudson.model.JDK.DescriptorImpl

    JDK.DescriptorImpl descriptor = ExtensionList.\
      lookupSingleton(JDK.DescriptorImpl.class)

    def desc = new hudson.model.JDK.DescriptorImpl()
    def jdks = []
    jdks = desc.getInstallations()

    assert jdks.size() == 3
    assert descriptor.getInstallations().toString().\
      contains('JDK[JDK8-update]')
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_global_properties_environment_no_change():
    groovy_script = """
    instance = Jenkins.getInstance()
    globalNodeProperties = instance.getGlobalNodeProperties()
    envVarsNodePropertyList = globalNodeProperties.\
      getAll(hudson.slaves.EnvironmentVariablesNodeProperty.class)

    assert envVarsNodePropertyList.get(0).getEnvVars().size()== 3
    assert envVarsNodePropertyList.get(0).getEnvVars().\
      get('FOO_BAR_no_change') \
      == 'http://foobar/repository/foobar-release/'

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_organization_folder_config_no_change():
    groovy_script = """
    def organizationFolderName = \
      "OFTEST-no-change"
    def organizationFolder = Jenkins.getInstance().\
      getItem(organizationFolderName)

    assert organizationFolder.\
      getDisplayName() == organizationFolderName

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_backup_plugin():
    groovy_script = """
    import jenkins.model.Jenkins
    import org.jvnet.hudson.plugins.thinbackup.ThinBackupMgmtLink

    def backackupPath = "/home/jenkins/jenkins_master_backup_new_path"
    def maxNumberToKeep = 4
    def backupSchedule = "0 0 * * 5"
    def timeout = 120
    def backupBuildResult = true
    def backupNextBuildNumber = true
    def moveOldBackupToZip = true

    def backupConfig = new ThinBackupMgmtLink()

    assert backupConfig.getConfiguration().getBackupPath() \
        == backackupPath
    assert backupConfig.getConfiguration().getNrMaxStoredFull() \
      == maxNumberToKeep
    assert backupConfig.getConfiguration().getFullBackupSchedule() \
      == backupSchedule
    assert backupConfig.getConfiguration().getForceQuietModeTimeout() \
      == timeout
    assert backupConfig.getConfiguration().isBackupBuildResults() \
      == backupBuildResult
    assert backupConfig.getConfiguration().isBackupNextBuildNumber() \
      == backupNextBuildNumber
    assert backupConfig.getConfiguration().isMoveOldBackupsToZipFile() \
      == moveOldBackupToZip
    return true
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_bitbucket_endpoint_update():
    groovy_script = """
    import jenkins.model.Jenkins
    import com.cloudbees.jenkins.plugins.bitbucket.endpoints.\
      BitbucketEndpointConfiguration
    import com.cloudbees.jenkins.plugins.bitbucket.endpoints.\
      BitbucketServerEndpoint
    import com.cloudbees.jenkins.plugins.bitbucket.server.\
      BitbucketServerWebhookImplementation

    def displayName = "foo-no-change"
    def serverUrl = "http://foobar.com:7990"
    def manageHook = "true".toBoolean()
    def credentialsId = "usr_pw_id"
    def callCanMerge = "true".toBoolean()
    def callChanges = "true".toBoolean()
    def webhookImplementation = "PLUGIN"
    def jenkins = Jenkins.getInstance()
    def globalConfig = jenkins.\
      getDescriptor(BitbucketEndpointConfiguration)
    def bitbucketEndpoint = globalConfig.\
      getEndpoints().find { endpoint ->
      endpoint.getDisplayName() == displayName
    }

    assert bitbucketEndpoint.getDisplayName() \
      == displayName
    assert bitbucketEndpoint.getServerUrl() \
      == serverUrl
    assert bitbucketEndpoint.isCallCanMerge() \
      == callCanMerge
    assert bitbucketEndpoint.isCallChanges() \
      == callChanges
    assert bitbucketEndpoint.isManageHooks() \
      == manageHook
    assert bitbucketEndpoint.getCredentialsId() \
      == credentialsId
    assert bitbucketEndpoint.getWebhookImplementation().toString() \
      == webhookImplementation

    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'


def test_project_matrix_authorization_strategy():
    groovy_script = """
    import jenkins.model.Jenkins
    import hudson.security.GlobalMatrixAuthorizationStrategy
    import hudson.security.ProjectMatrixAuthorizationStrategy
    import hudson.security.Permission

    def permissionMatrix = [
      "admin": [
          "hudson.model.Hudson.Administer",
      ],
      "bela": [
          "hudson.model.Hudson.Read",
          "hudson.model.Item.Read",
          "hudson.model.View.Read",
      ],
      "karoly": [
          "hudson.model.Hudson.Read",
          "hudson.model.Item.Read",
      ]
    ]

    class BuildPermission {
      static Map<Permission, String> buildNewAccessList( \
        String userOrGroup, List<String> permissions) {
        def newPermissionsMap = [:]
        permissions.each { permission ->
          newPermissionsMap.put(Permission.\
            fromId(permission), userOrGroup)
        }
        return newPermissionsMap
      }
    }

    def getAuthorizationInfo() {
      def jenkinsInstance = Jenkins.getInstance()
      def authorizationStrategy = jenkinsInstance.\
        getAuthorizationStrategy()

      if (authorizationStrategy \
        instanceof GlobalMatrixAuthorizationStrategy) {
        def matrixStrategy = \
          (GlobalMatrixAuthorizationStrategy) authorizationStrategy
        def permissionIds = matrixStrategy.getGrantedPermissions()

        return permissionIds
      }
    }

    strategy = new hudson.security.\
      ProjectMatrixAuthorizationStrategy()

    permissionMatrix.each { userOrGroup, capabilities ->
      accessList = BuildPermission.\
        buildNewAccessList(userOrGroup, capabilities)
      accessList.each {	p,u ->
        strategy.add(p, u)
      }
    }

    assert getAuthorizationInfo() == strategy.getGrantedPermissions()
    return 'true'
    """
    result = execute_and_wait_for_script_result(groovy_script)
    assert result == 'Result: true\n'

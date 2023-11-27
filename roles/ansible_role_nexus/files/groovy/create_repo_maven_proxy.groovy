import groovy.json.JsonSlurper
import org.sonatype.nexus.repository.manager.RepositoryManager
import org.sonatype.nexus.repository.config.Configuration

parsed_args = new JsonSlurper().parseText(args)

authentication = parsed_args.remote_username == null ? null : [
        type: 'username',
        username: parsed_args.remote_username,
        password: parsed_args.remote_password
]

def repositoryManager = repository.getRepositoryManager()

def existingRepository = repositoryManager.get(parsed_args.name)

if (existingRepository != null) {
    Configuration updatedConfiguration = existingRepository.configuration.copy().with {
                online = true

                attributes.maven.layoutPolicy = parsed_args.layout_policy.toUpperCase()

                attributes.proxy.remoteUrl = parsed_args.remote_url
                attributes.proxy.contentMaxAge = parsed_args.content_max_age
                attributes.proxy.metadataMaxAge = parsed_args.metadata_max_age

                attributes.httpclient.authentication = authentication

                attributes.negativeCache.timeToLive = parsed_args.time_to_live

                attributes.storage.strictContentTypeValidation = Boolean.valueOf(parsed_args.strict_content_validation)
                return it
        }
    
    repositoryManager.update(updatedConfiguration)
} else {
        def config
        try{
            config = repositoryManager.newConfiguration()
        }catch(MissingMethodException) {
            config = Configuration.newInstance()
        }
        config.with {
        repositoryName = parsed_args.name
        recipeName = 'maven2-proxy'
        online = true
        attributes = [
                maven  : [
                        versionPolicy: parsed_args.version_policy.toUpperCase(),
                        layoutPolicy : parsed_args.layout_policy.toUpperCase()
                ],
                proxy  : [
                        remoteUrl: parsed_args.remote_url,
                        contentMaxAge: parsed_args.content_max_age,
                        metadataMaxAge: parsed_args.metadata_max_age
                ],
                httpclient: [
                        blocked: false,
                        autoBlock: true,
                        authentication: authentication,
                        connection: [
                                useTrustStore: false
                        ]
                ],
                storage: [
                        blobStoreName: parsed_args.blob_store,
                        strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                ],
                negativeCache: [
                        enabled: true,
                        timeToLive: parsed_args.time_to_live
                ]
        ]
        }
    repositoryManager.create(config)
}

import groovy.json.JsonSlurper
import org.sonatype.nexus.repository.manager.RepositoryManager
import org.sonatype.nexus.repository.config.Configuration

parsed_args = new JsonSlurper().parseText(args)

def repositoryManager = repository.getRepositoryManager()

def existingRepository = repositoryManager.get(parsed_args.name)

if (existingRepository != null) {
    Configuration updatedConfiguration = existingRepository.configuration.copy().with {
      online = true
      attributes.group.memberNames = parsed_args.member_repos
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
            recipeName = 'npm-group'
            online = true
            attributes = [
                    group  : [
                            memberNames: parsed_args.member_repos
                    ],
                    storage: [
                            blobStoreName: parsed_args.blob_store,
                            strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                    ]
            ]
        }
    repositoryManager.create(config)
}
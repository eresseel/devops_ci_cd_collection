import groovy.json.JsonSlurper
import org.sonatype.nexus.repository.manager.RepositoryManager
import org.sonatype.nexus.repository.config.Configuration

parsed_args = new JsonSlurper().parseText(args)

def repositoryManager = repository.getRepositoryManager()

def existingRepository = repositoryManager.get(parsed_args.name)

def cleanupPolicies = parsed_args.cleanup_policies as Set

if (existingRepository != null) {
    Configuration updatedConfiguration = existingRepository.configuration.copy().with {
      online = true
      attributes.storage.writePolicy = parsed_args.write_policy.toUpperCase()
      attributes.storage.strictContentTypeValidation = Boolean.valueOf(parsed_args.strict_content_validation)

      if (cleanupPolicies != null) {
        attributes['cleanup'] = [policyName: cleanupPolicies]
      }
      
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
        recipeName = 'raw-hosted'
        online = true
        attributes = [
                storage: [
                        writePolicy: parsed_args.write_policy.toUpperCase(),
                        blobStoreName: parsed_args.blob_store,
                        strictContentTypeValidation: Boolean.valueOf(parsed_args.strict_content_validation)
                ]
        ]
        
        if (cleanupPolicies != null) {
            config.attributes['cleanup'] = [
                policyName: cleanupPolicies
            ]
        }
        }
    repositoryManager.create(config)
}

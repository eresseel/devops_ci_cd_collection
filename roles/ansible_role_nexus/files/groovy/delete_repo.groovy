import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

existingRepo = repository.getRepositoryManager().get(parsed_args.name)
if (existingRepo != null) {
    repository.getRepositoryManager().delete(parsed_args.name)
}
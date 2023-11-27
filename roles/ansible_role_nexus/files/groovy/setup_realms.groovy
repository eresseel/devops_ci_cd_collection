import groovy.json.JsonSlurper
import org.sonatype.nexus.security.realm.RealmManager

// parsed_args = new JsonSlurper().parseText(args)

realmManager = container.lookup(RealmManager.class.getName())
// enable Conan realm
realmManager.enableRealm("org.sonatype.repository.conan.internal.security.token.ConanTokenRealm", true)

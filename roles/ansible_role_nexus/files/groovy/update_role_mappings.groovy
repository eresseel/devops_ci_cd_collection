import groovy.json.JsonSlurper
import org.sonatype.nexus.security.SecuritySystem
import org.sonatype.nexus.security.role.RoleIdentifier
import org.sonatype.nexus.security.user.User
import org.sonatype.nexus.security.user.UserNotFoundException
import static org.sonatype.nexus.security.user.UserManager.DEFAULT_SOURCE


parsed_args = new JsonSlurper().parseText(args)

try {
    // update an existing user
    def securitySystem = security.getSecuritySystem()
    def realm = 'LDAP'
    def mappedRoles = parsed_args.roles
    if (mappedRoles?.size()) {
        User user = securitySystem.getUser(parsed_args.username, realm)
        user.roles.each {role ->
            if (role.source == realm) {
                mappedRoles.remove(role.roleId)
            }
        }
    }
    securitySystem.setUsersRoles(
            parsed_args.username,
            realm,
            mappedRoles?.size() > 0
                    ? mappedRoles?.collect {roleId -> new RoleIdentifier(DEFAULT_SOURCE, roleId)} as Set
                    : null
    )


} catch(UserNotFoundException ignored) {
    println "${ignored.message}"
}

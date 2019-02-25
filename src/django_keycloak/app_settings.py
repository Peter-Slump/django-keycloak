# Configure the model which need to be used to store the Open ID connect
# profile. There are two choices:
# - django_keycloak.OpenIdConnectProfile (Default) a local User object get
#   created for the logged in identity.
# - django_keycloak.RemoteUserOpenIdConnectProfile with this model there will
#   be no local user stored for the logged in identity.
KEYCLOAK_OIDC_PROFILE_MODEL = 'django_keycloak.OpenIdConnectProfile'

# Class which will be used as User object in case of the remote user OIDC
# Profile
KEYCLOAK_REMOTE_USER_MODEL = 'django_keycloak.remote_user.KeycloakRemoteUser'
KEYCLOAK_PERMISSIONS_METHOD = 'role'  # 'role' of 'resource'

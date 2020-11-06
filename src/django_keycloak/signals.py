from django.dispatch import Signal

# Allows clients to perform custom user population.
# Passed arguments: user
keycloak_populate_user = Signal()

from dynamic_fixtures.fixtures import BaseFixture

from django_keycloak.models import Realm, Server


class Fixture(BaseFixture):

    dependencies = (
        ('myapp', '0002_server'),
    )

    def load(self):
        server = Server.objects.get(url='https://identity.localhost.yarf.nl')

        Realm.objects.get_or_create(
            server=server,
            name='example',
            _certs='{"keys": [{"kid": "jr15h-1NMapltoxqLH8aBTD4-XjyfGD8pqUEtqsUJmU", "kty": "RSA", "alg": "RS256", "use": "sig", "n": "4hGf6zcb6KghN61pUROjPptdivncqkgaDcNwFcubw95Lw1IiTsgo__l1P3720Lhsb4Br0w2XWr44fzR8i1kgvow_s5-CG_F3S7OJ1Abz1Au_zSHg3nLd901lWMVrXvVZR1jFCuvIjr9DQAmyHv1-cL8OuBjGKWX7qi3LXQp2oEVRIUO_pM83vQJf1rZH-YUz6-w_g4XeOF-1GRXtaC2xYHbUCEsH1Lo7J-i3im4SgvER74Zh-cpoF_Q2DjK520VJletJBM4SrUh3DcScGVFmwharPI4wDdRXq_-SqQ52r1-X0k3fmj1gcwhLRH6jW0dTTt-T2ROENfjGTBBd5nBJWQ", "e": "AQAB"}]}',
            _well_known_oidc='{"issuer": "https://identity.localhost.yarf.nl/auth/realms/example", "authorization_endpoint": "https://identity.localhost.yarf.nl/auth/realms/example/protocol/openid-connect/auth", "token_endpoint": "https://identity.localhost.yarf.nl/auth/realms/example/protocol/openid-connect/token", "token_introspection_endpoint": "https://identity.localhost.yarf.nl/auth/realms/example/protocol/openid-connect/token/introspect", "userinfo_endpoint": "https://identity.localhost.yarf.nl/auth/realms/example/protocol/openid-connect/userinfo", "end_session_endpoint": "https://identity.localhost.yarf.nl/auth/realms/example/protocol/openid-connect/logout", "jwks_uri": "https://identity.localhost.yarf.nl/auth/realms/example/protocol/openid-connect/certs", "check_session_iframe": "https://identity.localhost.yarf.nl/auth/realms/example/protocol/openid-connect/login-status-iframe.html", "grant_types_supported": ["authorization_code", "implicit", "refresh_token", "password", "client_credentials"], "response_types_supported": ["code", "none", "id_token", "token", "id_token token", "code id_token", "code token", "code id_token token"], "subject_types_supported": ["public", "pairwise"], "id_token_signing_alg_values_supported": ["RS256"], "userinfo_signing_alg_values_supported": ["RS256"], "request_object_signing_alg_values_supported": ["none", "RS256"], "response_modes_supported": ["query", "fragment", "form_post"], "registration_endpoint": "https://identity.localhost.yarf.nl/auth/realms/example/clients-registrations/openid-connect", "token_endpoint_auth_methods_supported": ["private_key_jwt", "client_secret_basic", "client_secret_post"], "token_endpoint_auth_signing_alg_values_supported": ["RS256"], "claims_supported": ["sub", "iss", "auth_time", "name", "given_name", "family_name", "preferred_username", "email"], "claim_types_supported": ["normal"], "claims_parameter_supported": false, "scopes_supported": ["openid", "offline_access"], "request_parameter_supported": true, "request_uri_parameter_supported": true}'
        )

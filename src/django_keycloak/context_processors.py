def keycloak(request):
    if not hasattr(request, 'realm'):
        return {}

    realm = request.realm

    return {
        'op_location': realm.well_known_oidc['check_session_iframe'].replace(
            realm.server.internal_url,
            realm.server.url,
            1
        )
    }

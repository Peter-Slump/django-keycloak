from django.contrib.auth import SESSION_KEY, HASH_SESSION_KEY, BACKEND_SESSION_KEY, get_user_model, _get_backends
from django.contrib.auth.models import AnonymousUser
from django.middleware.csrf import rotate_token
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from django_keycloak.models import KeycloakRemoteUserOpenIDProfile


def _get_user_session_key(request):
    return str(request.session[SESSION_KEY])


def get_remote_user(request):
    """

    :param request:
    :return:
    """
    sub = request.session.get(SESSION_KEY)

    user = None

    try:
        oidc_profile = KeycloakRemoteUserOpenIDProfile.objects.get(realm=request.realm, sub=sub)

        if oidc_profile.refresh_expires_before > timezone.now():
            user = oidc_profile.user

    except KeycloakRemoteUserOpenIDProfile.DoesNotExist:
        pass

    return user or AnonymousUser()


def remote_user_login(request, user, backend=None):
    """
    Creates a session for the user.
    Based on the login function django.contrib.auth.login but uses a slightly different approach
    since the user is not backed by a database model.
    :param request:
    :param user:
    :param backend:
    :return:
    """
    session_auth_hash = ''
    if user is None:
        user = request.user

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.identifier:
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    if not hasattr(user, 'identifier'):
        raise ValueError(
            'The user does not have an identifier or the identifier is empty.'
        )

    request.session[SESSION_KEY] = id(user.identifier)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)
    # FIXME: This signal triggers some receivers that cannot handle the remote_user
    # user_logged_in.send(sender=user.__class__, request=request, user=user)

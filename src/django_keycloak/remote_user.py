from django.contrib import auth
from django.core.exceptions import PermissionDenied

from django_keycloak.models import RemoteUserOpenIdConnectProfile


class KeycloakRemoteUser(object):
    """
    A class based on django.contrib.auth.models.User.
    See https://docs.djangoproject.com/en/2.0/ref/contrib/auth/
    #django.contrib.auth.models.User
    """

    username = ''
    first_name = ''
    last_name = ''
    email = ''
    password = ''
    groups = []
    user_permissions = []

    _last_login = None

    def __init__(self, userinfo):
        """
        Create KeycloakRemoteUser from userinfo and oidc_profile.
        :param dict userinfo: the userinfo as retrieved from the OIDC provider
        """
        self.username = userinfo.get('preferred_username') or userinfo['sub']
        self.email = userinfo.get('email', '')
        self.first_name = userinfo.get('given_name', '')
        self.last_name = userinfo.get('family_name', '')
        self.sub = userinfo['sub']

    def __str__(self):
        return self.username

    @property
    def pk(self):
        """
        Since the BaseAbstractUser is a model, every instance needs a primary
        key. The Django authentication backend requires this.
        """
        return 0

    @property
    def identifier(self):
        """
        Identifier used for session storage.
        :rtype: str
        """
        return self.sub

    @property
    def is_staff(self):
        """
        :rtype: bool
        :return: whether the user is a staff member or not, defaults to False
        """
        return False

    @property
    def is_active(self):
        """
        :rtype: bool
        :return: whether the user is active or not, defaults to True
        """
        return True

    @property
    def is_superuser(self):
        """
        :rtype: bool
        :return: whether the user is a superuser or not, defaults to False
        """
        return False

    @property
    def last_login(self):
        """
        :rtype: Datetime
        :return: the date and time of the last login
        """
        return self._last_login

    @last_login.setter
    def last_login(self, content):
        """
        :param datetime content:
        """
        self._last_login = content

    @property
    def is_authenticated(self):
        """
        Read-only attribute which is always True.
        See https://docs.djangoproject.com/en/2.0/ref/contrib/auth/
        #django.contrib.auth.models.User.is_authenticated
        :return:
        """
        return True

    @property
    def is_anonymous(self):
        """
        Read-only attribute which is always False.
        See https://docs.djangoproject.com/en/2.0/ref/contrib/auth/
        #django.contrib.auth.models.User.is_anonymous
        :return:
        """
        return False

    def get_username(self):
        """
        Get the username
        :return: username
        """
        return self.username

    def get_full_name(self):
        """
        Get the full name (first name + last name) of the user.
        :return: the first name and last name of the user
        """
        return "{first} {last}".format(first=self.first_name,
                                       last=self.last_name)

    def get_short_name(self):
        """
        Get the first name of the user.
        :return: first name
        """
        return self.first_name

    def get_group_permissions(self, obj=None):
        pass

    def get_all_permissions(self, obj=None):
        """
        Logic from django.contrib.auth.models._user_get_all_permissions
        :param perm:
        :param obj:
        :return:
        """
        permissions = set()
        for backend in auth.get_backends():
            # Excluding Django.contrib.auth backends since they are not
            # compatible with non-db-backed permissions.
            if hasattr(backend, "get_all_permissions") \
                    and not backend.__module__.startswith('django.'):
                permissions.update(backend.get_all_permissions(self, obj))
        return permissions

    @property
    def oidc_profile(self):
        """
        Get the related OIDC Profile for this user.
        :rtype: django_keycloak.models.RemoteUserOpenIdConnectProfile
        :return: OpenID Connect Profile
        """
        try:
            return RemoteUserOpenIdConnectProfile.objects.get(sub=self.sub)
        except RemoteUserOpenIdConnectProfile.DoesNotExist:
            return None

    def has_perm(self, perm, obj=None):
        """
        Logic from django.contrib.auth.models._user_has_perm
        :param perm:
        :param obj:
        :return:
        """
        for backend in auth.get_backends():
            if not hasattr(backend, 'has_perm') \
                    or backend.__module__.startswith('django.contrib.auth'):
                continue
            try:
                if backend.has_perm(self, perm, obj):
                    return True
            except PermissionDenied:
                return False
        return False

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, module):
        """
        Logic from django.contrib.auth.models._user_has_module_perms
        :param module:
        :return:
        """
        for backend in auth.get_backends():
            if not hasattr(backend, 'has_module_perms'):
                continue
            try:
                if backend.has_module_perms(self, module):
                    return True
            except PermissionDenied:
                return False
        return False

    def email_user(self, subject, message, from_email=None, **kwargs):
        raise NotImplementedError('This feature is not implemented by default,'
                                  ' extend this class to implement')

    def save(self):
        """
        Normally implemented by django.db.models.Model
        :raises NotImplementedError: to remind that this is not a
        database-backed model and should not be used like one
        """
        raise NotImplementedError('This is not a database model')

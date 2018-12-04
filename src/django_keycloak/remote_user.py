from django.contrib import auth
from django.core.exceptions import PermissionDenied


class KeycloakRemoteUser(object):
    """
    A class based on django.contrib.auth.models.User.
    See https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#django.contrib.auth.models.User
    """

    username = ''
    first_name = ''
    last_name = ''
    email = ''
    password = ''
    groups = []
    user_permissions = []

    oidc_profile = None

    _last_login = None

    def __str__(self):
        return '%s@%s' % (self.username, self.oidc_profile.realm.name)

    @property
    def pk(self):
        """
        FIXME: This is included just to be sure, but if it is not necessary with the used backend, it should be removed.
        Since the BaseAbstractUser is a model, every instance needs a primary key.
        The Django authentication backend requires this.
        """
        return 0

    @property
    def identifier(self):
        """
        Identifier used for session storage.
        :rtype: str
        """
        return self.oidc_profile.sub

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
        :rtype: datetime
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
    def date_joined(self):
        """

        :rtype: DateTime
        :return: the date when the remote user joined
        """
        return ''

    @property
    def is_authenticated(self):
        """
        Read-only attribute which is always True.
        See https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#django.contrib.auth.models.User.is_authenticated
        :return:
        """
        return True

    @property
    def is_anonymous(self):
        """
        Read-only attribute which is always False.
        See https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#django.contrib.auth.models.User.is_anonymous
        :return:
        """
        return False

    def get_username(self):
        """

        :return: the username of the user
        """
        return self.username

    def get_full_name(self):
        """

        :return: the first name and last name of the user
        """
        return "{first} {last}".format(first=self.first_name, last=self.last_name)

    def get_short_name(self):
        """

        :return: the first name of the user
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
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(self, obj))
        return permissions

    def has_perm(self, perm, obj=None):
        """
        Logic from django.contrib.auth.models._user_has_perm
        :param perm:
        :param obj:
        :return:
        """
        for backend in auth.get_backends():
            if not hasattr(backend, 'has_perm'):
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
        raise NotImplementedError('This feature is not implemented by default, extend this class to implement')

    def save(self):
        """
        Normally implemented by django.db.models.Model
        :raises NotImplementedError: to remind that this is not a database-backed model and should not be used like one
        """
        raise NotImplementedError('This is not a database model')

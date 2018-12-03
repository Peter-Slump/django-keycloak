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

    def __init__(self):
        pass

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
        if self.oidc_profile:
            return "{},{}".format(self.oidc_profile.realm.name, self.oidc_profile.sub)

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

        :return:
        """
        return self._last_login

    @last_login.setter
    def last_login(self, content):
        """

        :param content:
        :return:
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
        pass

    def has_perm(self, obj=None):
        pass

    def has_perms(self, obj=None):
        pass

    def has_module_perms(self, obj=None):
        pass

    def email_user(self, subject, message, from_email=None, **kwargs):
        raise NotImplementedError('This feature is not implemented by default, extend this class to implement')

    def save(self):
        """
        Normally implemented by django.db.models.Model
        :raises NotImplementedError: to remind that this is not a database-backed model and should not be used like one
        """
        raise NotImplementedError('This is not a database model')

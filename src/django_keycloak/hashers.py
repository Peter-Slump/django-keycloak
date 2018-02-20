import hashlib

from django.contrib.auth.hashers import PBKDF2PasswordHasher


class PBKDF2SHA512PasswordHasher(PBKDF2PasswordHasher):

    algorithm = "pbkdf2_sha512"
    digest = hashlib.sha512

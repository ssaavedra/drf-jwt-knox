import jwt
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from knox.crypto import hash_token
from knox.models import AuthToken
from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)

from jwt_knox.settings import api_settings

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER
jwt_get_knox_token_from_payload = api_settings.JWT_PAYLOAD_GET_TOKEN_HANDLER


class BaseJWTTAuthentication(BaseAuthentication):
    """
    Token based authentication using Knox and JSON Web Token standard.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature is
        supplied and the underlying token exists on the database. Otherwise
        returns None.
        """
        decoded_token = self.get_jwt_value(request)
        if decoded_token is None:
            return None

        (user, auth_token) = self.authenticate_credentials(decoded_token)

        return (user, (decoded_token, auth_token))

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and token.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)
        token = jwt_get_knox_token_from_payload(payload)

        if not username or not token:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User inactive or deleted.')
            raise exceptions.AuthenticationFailed(msg)

        return (user, self.ensure_valid_auth_token(user, token))

    def ensure_valid_auth_token(self, user, token):
        for auth_token in AuthToken.objects.filter(user=user):
            if auth_token.expires is not None:
                if auth_token.expires < timezone.now():
                    auth_token.delete()
                    continue
            digest = hash_token(token, auth_token.salt)
            if digest == auth_token.digest:
                return auth_token

        msg = _('Invalid token.')
        raise exceptions.AuthenticationFailed(msg)


class JSONWebTokenKnoxAuthentication(BaseJWTTAuthentication):
    """
    Clients should authenticate by passing the JWT token in the "Authorization"
    HTTP header, prepended with the `JWT_AUTH_HEADER_PREFIX` string. For example:

      Authorization: Bearer abc.def.ghi
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should contain no spaces.')
            raise exceptions.AuthenticationFailed(msg)

        jwt_value = auth[1]

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        return payload

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of WWW-Authenticate
        header in a 401 Unauthorized response, or None if the
        authentication scheme should return 403 Permission Denied respones.
        """

        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX,
                                        self.www_authenticate_realm)

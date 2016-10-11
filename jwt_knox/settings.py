import datetime

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'JWT_AUTH', None)

DEFAULTS = {
    'JWT_LOGIN_AUTHENTICATION_CLASSES': settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'],
    'JWT_ENCODE_HANDLER': 'jwt_knox.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER': 'jwt_knox.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER': 'jwt_knox.utils.jwt_payload_handler',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'jwt_knox.utils.jwt_get_username_from_payload_handler',
    'JWT_PAYLOAD_GET_TOKEN_HANDLER': 'jwt_knox.utils.jwt_get_token_from_payload_handler',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'jwt_knox.utils.jwt_response_payload_handler',
    'JWT_SECRET_KEY': settings.SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_VERIFY': True,
    'JWT_LEEWAY': 0,
}

IMPORT_STRINGS = (
    'JWT_LOGIN_AUTHENTICATION_CLASSES',
    'JWT_ENCODE_HANDLER',
    'JWT_DECODE_HANDLER',
    'JWT_PAYLOAD_HANDLER',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER',
    'JWT_PAYLOAD_GET_TOKEN_HANDLER',
    'JWT_RESPONSE_PAYLOAD_HANDLER',
)


api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


import jwt
import uuid
from calendar import timegm
from datetime import datetime

from django.contrib.auth import get_user_model

from knox.models import AuthToken

from jwt_knox.settings import api_settings


def get_username_field():
    try:
        username_field = get_user_model().USERNAME_FIELD
    except:
        username_field = 'username'

    return username_field


def get_username(user):
    try:
        username = user.get_username()
    except AttributeError:
        username = user.username

    return username


def create_auth_token(user, expires):
    auth_token = AuthToken.objects.create(user=user, expires=expires)
    payload = jwt_payload_handler(user, auth_token, expires)

    return jwt_encode_handler(payload)


def jwt_get_token_from_payload_handler(payload):
    return payload.get('jti')


def jwt_get_username_from_payload_handler(payload):
    return payload.get('username')


def jwt_payload_handler(user, token, expires):
    username_field = get_username_field()
    username = get_username(user)

    payload = {
        'username': username,
        'iat': timegm(datetime.utcnow().utctimetuple()),
        'jti': token,
    }

    if expires:
        payload['exp'] = datetime.utcnow() + expires

    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    payload[username_field] = username

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


def jwt_encode_handler(payload):
    return jwt.encode(payload, api_settings.JWT_SECRET_KEY,
                      api_settings.JWT_ALGORITHM).decode('utf-8')


def jwt_decode_handler(token):
    options = {'verify_exp': True, }

    return jwt.decode(
        token,
        api_settings.JWT_SECRET_KEY,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM], )


def jwt_join_header_and_token(token):
    return "{0} {1}".format(api_settings.JWT_AUTH_HEADER_PREFIX,
                            token, )


def jwt_response_payload_handler(token, user=None, request=None):
    return {'token': jwt_join_header_and_token(token), }

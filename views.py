from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jwt_knox.auth import JSONWebTokenKnoxAuthentication
from jwt_knox.settings import api_settings
from jwt_knox.utils import create_auth_token


response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

class JWTKnoxAPIView(APIView):
    """
    Base class for JWT-Knox tokens. Redefines authentication and
    permission classes so that these views can only be authenticated
    with a JWT Knox token.
    """
    authentication_classes = (JSONWebTokenKnoxAuthentication,)
    permission_classes = (IsAuthenticated,)

class LoginView(APIView):
    """
    This view authenticates a user via the
    JWT_LOGIN_AUTHENTICATION_CLASSES (which, in turn, defaults to
    rest_framework's DEFAULT_AUTHENTICATION_CLASSES) to get a view
    token.

    """
    authentication_classes = api_settings.JWT_LOGIN_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({"msg": "Use a POST request to access this resource."})

    def post(self, request, expires=None):
        token = create_auth_token(user=request.user, expires=expires)
        return Response(response_payload_handler(token, request.user, request))

class VerifyView(JWTKnoxAPIView):
    """
    This view allows a third party to verify a web token.
    """
    def get(self, request):
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        return self.get(request)

class DebugVerifyTokenView(JWTKnoxAPIView):
    """
    This view returns internal data on the token, the user and the current
    request.
    NOT TO BE USED IN PROUDCTION.
    """
    def get(self, request):
        token = request.auth[0]
        return Response(response_payload_handler(token, request.user, request),
                        status=status.HTTP_200_OK)

class LogoutView(JWTKnoxAPIView):
    """
    Invalidates the current token, so that it cannot be used anymore
    for authentication.
    """
    def post(self, request):
        request.auth[1].delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LogoutOtherView(JWTKnoxAPIView):
    """
    Invalidates all the tokens except the current one, so that all other
    remaining open sessions get closed and only the current one is still
    open.
    """
    def post(self, request):
        tokens_to_delete = request.user.auth_token_set.exclude(pk=request.auth[1].pk)
        num = tokens_to_delete.delete()
        return Response({"deleted_sessions": num[0]})


class LogoutAllView(JWTKnoxAPIView):
    """
    Invalidates all currently valid tokens for the user, including the
    current session. This endpoint invalidates the current token, and you
    will need to authenticate again.
    """
    def post(self, request):
        request.user.auth_token_set.all().delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

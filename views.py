from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from knox.models import AuthToken
from knox.settings import knox_settings

from jwt_knox.auth import JSONWebTokenKnoxAuthentication
from jwt_knox.settings import api_settings
from jwt_knox.utils import create_auth_token


response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

class JWTKnoxAPIView(APIView):
    authentication_classes = (JSONWebTokenKnoxAuthentication,)
    permission_classes = (IsAuthenticated,)

class LoginView(APIView):
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
    def get(self, request):
        token = request.auth[0]
        return Response(response_payload_handler(token, request.user, request),
                        status=status.HTTP_200_OK)

class LogoutView(JWTKnoxAPIView):
    def post(self, request):
        request.auth[1].delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LogoutOtherView(JWTKnoxAPIView):
    def post(self, request):
        tokens_to_delete = request.user.auth_token_set.exclude(pk=request.auth[1].pk)
        num = tokens_to_delete.delete()
        return Response({"deleted_sessions": num[0]})


class LogoutAllView(JWTKnoxAPIView):
    def post(self, request):
        request.user.auth_token_set.all().delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from jwt_knox.auth import JSONWebTokenKnoxAuthentication
from jwt_knox.settings import api_settings
from jwt_knox.utils import create_auth_token

response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

class PerViewAuthenticatorMixin(object):
    def initial(self, request, *args, **kwargs):
        """
        Reinitialize self.request so that it gets the correct authenticators again.
        """
        self.request = request = self.initialize_request(request, *args, **kwargs)
        return super(PerViewAuthenticatorMixin, self).initial(request, *args, **kwargs)

    def get_authenticators(self):
        """
        First tries to get the specific authenticators for a view by
        calling `.get_authenticators_for_view`, but falls back on the
        class's authenticators.
        """
        authenticators = self.authentication_classes or ()

        if hasattr(self, 'action'):
            # action gets populated on the second time we are called
            per_view = self.get_authenticators_for_view(self.action)
            if per_view is not None:
                authenticators = per_view

        return [auth() for auth in authenticators]

    def get_authenticators_for_view(self, view_name):
        """
        Define the authenticators present in a specific view.
        """
        pass


class JWTKnoxAPIViewSet(PerViewAuthenticatorMixin, ViewSet):
    """This API endpoint set enables authentication via **JSON Web Tokens** (JWT).

    The provided JWTs are meant for a single device only and to be
    kept secret. The tokens may be set to expire after a certain time
    (see `get_token`). The tokens may be revoked in the server via the
    diverse logout endpoints. The JWTs are database-backed and may be
    revoked at any time.
    """
    base_name = 'jwt_knox'

    authentication_classes = (JSONWebTokenKnoxAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_authenticators_for_view(self, view_name):
        if view_name == 'get_token':
            return api_settings.JWT_LOGIN_AUTHENTICATION_CLASSES

    @list_route(methods=['post', ])
    def get_token(self, request, expires=None):
        """
        This view authenticates a user via the
        `JWT_LOGIN_AUTHENTICATION_CLASSES` (which, in turn, defaults to
        rest_framework's `DEFAULT_AUTHENTICATION_CLASSES`) to get a view
        token.
        """
        token = create_auth_token(user=request.user, expires=expires)
        return Response(response_payload_handler(token, request.user, request))

    @list_route(methods=('get', 'post'))
    def verify(self, request):
        """
        This view allows a third party to verify a web token.
        """
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=('get', ))
    def debug_verify(self, request):
        """
        This view returns internal data on the token, the user and the current
        request.

        **NOT TO BE USED IN PROUDCTION.**
        """
        token = request.auth[0]
        return Response(
            response_payload_handler(token, request.user, request),
            status=status.HTTP_200_OK)

    @list_route(methods=('post', ))
    def logout(self, request):
        """
        Invalidates the current token, so that it cannot be used anymore
        for authentication.
        """
        request.auth[1].delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=('post', ))
    def logout_other(self, request):
        """
        Invalidates all the tokens except the current one, so that all other
        remaining open sessions get closed and only the current one is still
        open.
        """
        tokens_to_delete = request.user.auth_token_set.exclude(
            pk=request.auth[1].pk)
        num = tokens_to_delete.delete()
        return Response({"deleted_sessions": num[0]})

    @list_route(methods=('post', ))
    def logout_all(self, request):
        """
        Invalidates all currently valid tokens for the user, including the
        current session. This endpoint invalidates the current token, and you
        will need to authenticate again.
        """
        request.user.auth_token_set.all().delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

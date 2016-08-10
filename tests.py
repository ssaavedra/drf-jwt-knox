from django.core.urlresolvers import reverse
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from .settings import api_settings


class APIAuthTest(APITestCase):

    # Our default user's credentials
    username = 'prova1'
    email = ''
    password = 'usuario123'
    test_logout_all_client_number = 3

    # Used URLs
    login_url = reverse('jwt_knox:get_new_token')
    verify_url = reverse('jwt_knox:verify_token')
    logout_current_url = reverse('jwt_knox:logout_current_token')
    logout_other_url = reverse('jwt_knox:logout_other_tokens')
    logout_all_url = reverse('jwt_knox:logout_all_user_tokens')

    def setUp(self):
        """
        Before each test, run the create_test_user fixture
        """
        self.fixture_create_test_user()

    def fixture_create_test_user(self):
        """
        Adds the default user to the database
        :return:
        """
        User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def with_token(self, token):
        if not token:
            self.client.credentials(HTTP_AUTHORIZATION=None)
            return self

        auth_header = "{prefix} {token}".format(
            prefix=api_settings.JWT_AUTH_HEADER_PREFIX,
            token=token
        )

        self.client.credentials(HTTP_AUTHORIZATION=auth_header)

        return self

    def verify_token(self, token):
        return self.with_token(token).client.post(self.verify_url)

    def logout_current(self, token=None):
        if token:
            self.with_token(token)
        return self.client.post(self.logout_current_url)

    def logout_other(self):
        return self.client.post(self.logout_other_url)

    def logout_all(self):
        return self.client.post(self.logout_all_url)

    def get_token(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(self.login_url)
        return response

    def get_n_tokens(self,n):
        """
        This method allows to get an arbitrary number of tokens for a logged client
        :param n: Number of tokens we want to get
        :return:
        """
        response_list = []
        self.client.login(username=self.username, password=self.password)
        for i in range (0,n):
            response = self.client.post(self.login_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_list.append(response)
        return response_list

    @staticmethod
    def build_auth_header(token):
        """
        This method allows to build the authentication header that a client could use for his future requests.
        :param token: the token we want to use to authenticate the client
        :return:
        """
        header = "{prefix} {token}".format(prefix=api_settings.JWT_AUTH_HEADER_PREFIX,
                                           token=token)
        return header

    def test_get_token(self):
        """
        Verify that our 'get_token' endpoint is working properly
        :return:
        """
        response = self.get_token()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        """
        Verify that our 'logout' endpoint is logging out properly
        :return:
        """
        login_response = self.get_token()
        token = login_response.data['token']
        logout_response = self.with_token(token).logout_current()
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_double_login(self):
        """
        This test proves that if a user can log in twice and the two tokens he will be provided are different
        :return:
        """
        # Warning, in the next few lines we are using 'magic numbers'
        response_list = self.get_n_tokens(2)
        token1 = response_list[0].data['token']
        token2 = response_list[1].data['token']
        self.assertEqual(response_list[0].status_code, status.HTTP_200_OK)
        self.assertEqual(response_list[1].status_code, status.HTTP_200_OK)
        self.assertNotEqual(token1, token2)

    def test_double_logout(self):
        """
        Here we prove that after logging out once, the endpoint will reject a second logout request
        :return:
        """
        login_response = self.get_token()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data['token']
        logout_response1 = self.with_token(token).logout_current()
        logout_response2 = self.with_token(token).logout_current()
        self.assertEqual(logout_response1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(logout_response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_old_token(self):
        """
        This test verifies that after logging out, the token we used becomes invalid
        :return:
        """
        login_response = self.get_token()
        token = login_response.data['token']
        logout_response = self.with_token(token).logout_current()
        verify_response = self.verify_token(token)
        self.assertEqual(verify_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_non_logged(self):
        """
        This test verifies that the "logout" endpoint will reject request from non-logged clients
        :return:
        """
        response = self.logout_current()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_old_token(self):
        """
        Here we prove that a client can't use an expired token to logout even
        if logged in again with a different one

        :return:
        """
        token1 = self.get_token().data['token']
        self.with_token(token1).logout_current()
        token2 = self.get_token().data['token']
        self.assertNotEqual(token1, token2)
        response2 = self.with_token(token1).logout_current()
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

        # We can eventually go on and verify if we're still logged
        # and if we can finally log out using the second token
        response3 = self.with_token(token2).logout_current()
        self.assertEqual(response3.status_code, status.HTTP_204_NO_CONTENT)

    def test_verify(self):
        """
        A simple test against or 'verify' endpoint
        :return:
        """
        token_response = self.get_token()
        token = token_response.data['token']
        response = self.verify_token(token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_close_other_access(self):
        """
        During this test a client obtains 2 tokens and we prove that authenticating with just one of them
        he's able to invalidate the other one using the 'logout_other' endpoint
        :return:
        """
        # Warning, in the next 3 lines we're using 'magic numbers'
        response_list = self.get_n_tokens(2)
        token1 = response_list[0].data['token']
        token2 = response_list[1].data['token']
        response3 = self.with_token(token1).logout_other()
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        response4 = self.verify_token(token1)
        self.assertEqual(response4.status_code, status.HTTP_204_NO_CONTENT)
        response5 = self.verify_token(token2)
        self.assertEqual(response5.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_all(self):
        """
        In this test we prove that a single request against the 'logout_all' endpoint will invalidate all the tokens
        related to a single user
        :return:
        """
        token_list = []
        response_list = self.get_n_tokens(self.test_logout_all_client_number)
        for i in range(0,self.test_logout_all_client_number):
            token = response_list[i].data['token']
            token_list.append(token)
        logout_response = self.with_token(token_list[0]).logout_all()
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        for i in range(0,self.test_logout_all_client_number):
            response = self.verify_token(token_list[i])
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

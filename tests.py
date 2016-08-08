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

    def create_test_user(self):
        """
        Adds the default user to the database
        :return:
        """
        User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def get_token(self):
        self.create_test_user()
        myurl = reverse('jwt_knox:get_new_token')
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(myurl)
        return response

    def get_n_tokens(self,n):
        """
        This method allows to get an arbitrary number of tokens for a logged client
        :param n: Number of tokens we want to get
        :return:
        """
        self.create_test_user()
        response_list = []
        myurl = reverse('jwt_knox:get_new_token')
        self.client.login(username=self.username, password=self.password)
        for i in range (0,n):
            response = self.client.post(myurl)
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
        url = reverse('jwt_knox:logout_current_token')
        login_response = self.get_token()
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(token))
        logout_response = self.client.post(url)
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
        url = reverse('jwt_knox:logout_current_token')
        login_response = self.get_token()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(token))
        logout_response1 = self.client.post(url, {}, format='json')
        logout_response2 = self.client.post(url, {}, format='json')
        self.assertEqual(logout_response1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(logout_response2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_old_token(self):
        """
        This test verifies that after logging out, the token we used becomes invalid
        :return:
        """
        logout_url = reverse ('jwt_knox:logout_current_token')
        verify_url = reverse ('jwt_knox:verify_token')
        login_response = self.get_token()
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(token))
        logout_response = self.client.post(logout_url)
        verify_response = self.client.post(verify_url)
        self.assertEqual(verify_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_non_logged(self):
        """
        This test verifies that the "logout" endpoint will reject request from non-logged clients
        :return:
        """
        url = reverse('jwt_knox:logout_current_token')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_old_token(self):
        """
        Here we prove that a client can't use an old token to logout even if it logged in again
        :return:
        """
        login_url = reverse('jwt_knox:get_new_token')
        logout_url = reverse('jwt_knox:logout_current_token')
        login_response = self.get_token()
        first_token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(first_token))
        self.client.post(logout_url)
        response1 = self.client.post(login_url)
        second_token = response1.data['token']
        self.assertNotEqual(first_token, second_token)
        response2 = self.client.post(logout_url)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

        # We can eventually go on and verify if we're still logged
        # and if we can finally log out using the second token
        self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(second_token))
        response3 = self.client.post(logout_url)
        self.assertEqual(response3.status_code, status.HTTP_204_NO_CONTENT)

    def test_verify(self):
        """
        A simple test against or 'verify' endpoint
        :return:
        """
        url = reverse('jwt_knox:verify_token')
        token_response = self.get_token()
        token = token_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(token))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_close_other_access(self):
        """
        During this test a client obtains 2 tokens and we prove that authenticating with just one of them
        he's able to invalidate the other one using the 'logout_other' endpoint
        :return:
        """
        login_url = reverse('jwt_knox:get_new_token')
        verify_url = reverse('jwt_knox:verify_token')
        logout_other = reverse('jwt_knox:logout_other_tokens')
        # Warning, in the next 3 lines we're using 'magic numbers'
        response_list = self.get_n_tokens(2)
        token1 = response_list[0].data['token']
        token2 = response_list[1].data['token']
        self.client.credentials(HTTP_AUTHORIZATION=api_settings.JWT_AUTH_HEADER_PREFIX + ' ' + token1)
        response3 = self.client.post(logout_other)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        response4 = self.client.post(verify_url)
        self.assertEqual(response4.status_code, status.HTTP_204_NO_CONTENT)
        self.client.credentials(HTTP_AUTHORIZATION=api_settings.JWT_AUTH_HEADER_PREFIX + ' ' + token2)
        response5 = self.client.post(verify_url)
        self.assertEqual(response5.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_all(self):
        """
        In this test we prove that a single request against the 'logout_all' endpoint will invalidate all the tokens
        related to a single user
        :return:
        """
        verify_url = reverse('jwt_knox:verify_token')
        logout_all_url = reverse('jwt_knox:logout_all_user_tokens')
        token_list = []
        response_list = self.get_n_tokens(self.test_logout_all_client_number)
        for i in range(0,self.test_logout_all_client_number):
            token = response_list[i].data['token']
            token_list.append(token)
        self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(token_list[0]))
        logout_response = self.client.post(logout_all_url)
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        for i in range(0,self.test_logout_all_client_number):
            self.client.credentials(HTTP_AUTHORIZATION=self.build_auth_header(token_list[i]))
            response = self.client.post(verify_url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Song, Level


class APIAuthTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(APIAuthTest, cls).setUpClass()
        cls.user = 'user'
        User.objects.create_user(cls.user, 'some@email.com', cls.user)

        cls.user_credentials = {
            'username': cls.user,
            'password': cls.user
        }

        token = lambda self: self.client.post('/auth/token/', data=cls.user_credentials, format='json').json()['token']
        cls.auth_header = lambda self: {'authorization': 'Bearer %s' % token(self)}

    def test_ok_get_token(self):
        response = self.client.post('/auth/token/', data=self.user_credentials)
        self.assertIn('token', response.data)
        self.assertIn('expiration', response.data)
        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_wrong_credentials_get_token(self):
        wrong_credentials = {
            'username': self.user,
            'password': 'somewrongpassword'
        }
        response = self.client.post('/auth/token/', data=wrong_credentials)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_no_credentials_get_token(self):
        response = self.client.post('/auth/token/', data={})
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_ok_refresh_token(self):
        response = self.client.post('/auth/token-refresh/', headers=self.auth_header())
        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_no_token_refresh_token(self):
        response = self.client.post('/auth/token-refresh/')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_wrong_token_refresh_token(self):
        response = self.client.post('/auth/token-refresh/', headers={'authorization': 'Bearer somewrongtoken'})
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_ok_register_new_user(self):
        new_user = 'new_user'
        new_user_data = {
            'first_name': new_user,
            'last_name': new_user,
            'username': new_user,
            'email': 'e@mail.com',
            'password': new_user
        }

        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEquals(status.HTTP_200_OK, response.status_code)

        response_should_contain = {
            'first_name', 'last_name', 'username', 'email'
        }

        for field in response_should_contain:
            self.assertIn(field, response.data)

    def test_wrong_params_register_new_user(self):
        new_user = 'some_new_user'
        new_user_data = {
            'username': new_user,
            'password': new_user
        }

        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_multiple_register_new_user(self):
        new_user = 'new_user'
        new_user_data = {
            'first_name': new_user,
            'last_name': new_user,
            'username': new_user,
            'email': 'e@mail.com',
            'password': new_user
        }

        self.client.post('/auth/register/', data=new_user_data)
        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def tearDown(self):
        self.client.cookies.clear()
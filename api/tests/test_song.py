from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Song, Level


class APISongsTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(APISongsTest, cls).setUpClass()
        cls.user = 'user'
        User.objects.create_user(cls.user, 'some@email.com', cls.user)

        user_credentials = {
            'username': cls.user,
            'password': cls.user
        }

        token = lambda self: self.client.post('/auth/token/', data=user_credentials, format='json').json()['token']
        cls.auth_header = lambda self: {'authorization': 'Bearer %s' % token(self)}

        # Add levels
        levels = [Level(name=lvl) for lvl in ['Easy', 'Medium', 'Difficult']]

        Level.objects.bulk_create(levels)

        # Add song
        song = {
            'name': 'Eine Kleine',
            'file': 'songs/mozart_eine_kleine_easy.mid',
            'level': Level.objects.get(id=1),
            'length': 'Short'
        }
        song_model = Song.objects.create(**song)

    def test_ok_get_songs(self):
        response = self.client.get('/songs/', format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_data_get_songs(self):
        response = self.client.get('/songs/', format='json', headers=self.auth_header())
        response_json_expected = [
            {
                'id': 1,
                'name': 'Eine Kleine',
                'level': 'Easy',
                'length': 'Short'
            }
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), response_json_expected)

    def test_no_token_get_song(self):
        response = self.client.get('/songs/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_token_get_song(self):
        response = self.client.get('/songs/', format='json', headers={'authorizarion': 'Bearer '})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ok_download_songs(self):
        params = {
            'song_id': 1
        }

        response = self.client.get('/songs/download/', data=params, format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_params_download_songs(self):
        params = {'asdasd': 15}

        response = self.client.get('/songs/download/', data=params, format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_params_download_songs(self):
        response = self.client.get('/songs/download/', data={}, format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_download_song(self):
        params = {
            'song_id': 1
        }

        fields_required_in_song_json = {
            'total_time',
            'qpm',
            'notes'
        }

        note_body_should_contain = {
            'pitch',
            'start_time',
            'end_time',
            'velocity'
        }

        response = self.client.get('/songs/download/', data=params, format='json', headers=self.auth_header())

        for field in fields_required_in_song_json:
            self.assertIn(field, response.data)

        for note_field in note_body_should_contain:
            self.assertIn(note_field, response.data['notes'][0])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_token_download_song(self):
        params = {
            'song_id': 1
        }
        response = self.client.get('/songs/download/', data=params, format='json', headers={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ok_create_song(self):
        params = {
            'song_id': 1,
            'start_time': 0.0,
            'stop_time': 10.0
        }

        response = self.client.get('/songs/create_song/', data=params, format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_parameters_create_song(self):
        params = {
            'song_id': 1,
            'start_time': 0.0,
        }

        response = self.client.get('/songs/create_song/', data=params, format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_parameters_create_song(self):
        response = self.client.get('/songs/create_song/', data={}, format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_data_create_song(self):
        song_id = 1
        start_time = 0.0
        stop_time = 10.0

        params = {
            'song_id': song_id,
            'start_time': start_time,
            'stop_time': stop_time
        }

        response_should_contain = {
            'notes', 'qpm', 'total_time'
        }

        note_should_contain = {
            'start_time', 'end_time', 'velocity', 'pitch'
        }

        response = self.client.get('/songs/create_song/', data=params, format='json', headers=self.auth_header())
        for field in response_should_contain:
            self.assertIn(field, response.data)

        for note_field in note_should_contain:
            self.assertIn(note_field, response.data['notes'][0])

        self.assertAlmostEqual(stop_time-start_time, response.data['total_time'], 0)

    def test_no_token_create_song(self):
        song_id = 1
        start_time = 0.0
        stop_time = 10.0

        params = {
            'song_id': song_id,
            'start_time': start_time,
            'stop_time': stop_time
        }

        response = self.client.get('/songs/create_song/', data=params, format='json', headers={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        self.client.cookies.clear()

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Song, Level, SongStat


class APISongStatsTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(APISongStatsTest, cls).setUpClass()
        cls.user = 'user'
        cls.user_object = User.objects.create_user(cls.user, 'some@email.com', cls.user)

        user_credentials = {
            'username': cls.user,
            'password': cls.user
        }

        token = lambda self: self.client.post('/auth/token/', data=user_credentials, format='json').json()['token']
        cls.auth_header = lambda self: {'authorization': 'Bearer %s' % token(self)}

        # Add levels
        levels = ['Easy', 'Medium', 'Difficult']
        Level.objects.bulk_create(Level(name=lvl) for lvl in levels)

        # Add song
        song = {
            'name': 'Eine Kleine',
            'file': 'songs/mozart_eine_kleine_easy.mid',
            'level': Level.objects.get(name=levels[0]),
            'length': 'Short'
        }
        cls.song_object = Song.objects.create(**song)

        # Add some progresses
        cls.high_scores = [2, 1, 1, 3, 2, 1]
        cls.practice_time = [12, 7, 4, 20, 6, 32]
        cls.song_stats_objects = [
            SongStat(
                user=cls.user_object,
                high_score=cls.high_scores[i],
                practice_time=cls.practice_time[i],
                song=cls.song_object
            ) for i in range(len(cls.high_scores))
        ]
        SongStat.objects.bulk_create(cls.song_stats_objects)

    def test_ok_user_song_stats(self):
        response = self.client.get('/songstats/', format='json', headers=self.auth_header())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_data_user_song_stats(self):
        response_should_contain = {
            'user_id', 'time_spent_practicing', 'high_score', 'song_name', 'last_practice'
        }

        response = self.client.get('/songstats/', format='json', headers=self.auth_header())

        for field in response_should_contain:
            self.assertIn(field, response.data)

        self.assertEqual(self.song_object.name, response.data['song_name'])
        self.assertEqual(max(self.high_scores), response.data['high_score'])
        self.assertEqual(sum(self.practice_time), response.data['time_spent_practicing'])
        self.assertEqual(self.user_object.id, response.data['user_id'])

    def test_no_token_user_song_stats(self):
        response = self.client.get('/songstats/', format='json', headers={})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_add_song_stats(self):
        test_user = 'test_add_song'
        test_user_model = User.objects.create_user(test_user, 'e@mail.com', test_user)

        test_credentials = {
            'username': test_user,
            'password': test_user
        }
        token = self.client.post('/auth/token/', data=test_credentials, format='json').json()['token']

        response = self.client.post(
            '/songstats/?song_id=%s&practice_time=%s&high_score=%s' % (self.song_object.id, 42, 3),
            headers={'authorization': 'Bearer %s' % token}
        )

        response_should_contain = {
            'id', 'song_name', 'practice_time', 'high_score', 'created_at', 'user', 'song'
        }

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        for field in response_should_contain:
            self.assertIn(field, response.data)

        self.assertEqual(42, response.data['practice_time'])
        self.assertEqual(3, response.data['high_score'])
        self.assertEqual(test_user_model.id, response.data['user'])

    def test_no_token_add_song_stats(self):
        response = self.client.post('/songstats/')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_ok_all_song_progress_for_current_user(self):
        response = self.client.get('/songstats/all_songs/', headers=self.auth_header())
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_data_all_song_progress_for_current_user(self):
        song_should_contain = {
            'song_id', 'high_score'
        }

        response = self.client.get('/songstats/all_songs/', headers=self.auth_header())

        self.assertEquals(list, type(response.data))

        for field in song_should_contain:
            self.assertIn(field, response.data[0])

    def test_no_token_song_progress_for_current_user(self):
        response = self.client.get('/songstats/all_songs/', headers={})
        self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def tearDown(self):
        self.client.cookies.clear()

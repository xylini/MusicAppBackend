import jwt
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.exceptions.generic import RequiredDataNotProvidedException
from api.models import SongStat
from api.serializers.songstat import SongStatSerializer


class SongStatViewSet(viewsets.ViewSet):
    def list(self, request):
        user_id = jwt.decode(request.auth, verify=False)['user_id']
        practice_time_sum = SongStat.objects.filter(user_id=user_id).aggregate(Sum('practice_time'))['practice_time__sum']
        best_song = SongStat.objects.filter(user_id=user_id).order_by('-high_score').first()
        last_practice = SongStat.objects.order_by('-created_at').first()

        response_data = {
            'user_id': user_id,
            'time_spent_practicing': 0,
            'high_score': 0,
            'song_name': None,
            'last_practice': None
        }

        if best_song is not None:
            best_song_serialized = SongStatSerializer(best_song).data
            last_practice = SongStatSerializer(last_practice).data

            response_data['time_spent_practicing'] = practice_time_sum
            response_data['high_score'] = best_song_serialized['high_score']
            response_data['song_name'] = best_song_serialized['song_name']
            response_data['last_practice'] = last_practice['created_at']

        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        is_whole_data_provided = len({'practice_time', 'high_score', 'song_id'} - set(data)) == 0
        user_id = jwt.decode(request.auth, verify=False)['user_id']

        if not is_whole_data_provided:
            raise RequiredDataNotProvidedException

        song_stat_entity = SongStat(
            user_id=user_id,
            high_score=data['high_score'],
            song_id=data['song_id'],
            practice_time=data['practice_time']
        )

        song_stat_entity.save()

        song_stat_serialized = SongStatSerializer(song_stat_entity).data

        return Response(song_stat_serialized, status=status.HTTP_200_OK)

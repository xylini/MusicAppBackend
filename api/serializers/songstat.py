from rest_framework import serializers
from api.models import SongStat


class SongStatSerializer(serializers.ModelSerializer):
    song_name = serializers.ReadOnlyField(source='song.name')

    class Meta:
        model = SongStat
        fields = '__all__'

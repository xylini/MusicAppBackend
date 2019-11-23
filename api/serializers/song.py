from rest_framework import serializers
from api.models import Song


class SongSerializer(serializers.ModelSerializer):
    level = serializers.ReadOnlyField(source='level.name')

    class Meta:
        model = Song
        fields = ('id', 'name', 'level', 'length')


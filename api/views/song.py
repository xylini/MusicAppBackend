from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.exceptions.song import SongDoesNotExistsException, RequiredParamsNotProvidedException
from api.models import Song
from api.serializers.song import SongSerializer
from music_app_backend.settings import MEDIA_ROOT

import magenta.music as mm
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.music import midi_file_to_note_sequence
from magenta.protobuf import generator_pb2
from magenta.music.sequences_lib import extract_subsequence


class SongViewSet(viewsets.ViewSet):
    def list(self, request):
        songs = Song.objects.all()
        songs_serialized = SongSerializer(songs, many=True)

        return Response(songs_serialized.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def download(self, request):
        is_required_params = 'song_id' in request.query_params
        if not is_required_params:
            raise RequiredParamsNotProvidedException

        file_path = self.get_song_file_path(request.query_params.get('song_id'))
        note_sequence = midi_file_to_note_sequence(file_path)
        prepared_song = note_sequence_to_note_list(note_sequence)

        return Response(data=prepared_song, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def create_song(self, request):
        params = set(request.query_params)
        required_params = {'song_id', 'start_time', 'stop_time'}
        are_required_params = len(required_params - params) == 0

        if not are_required_params:
            raise RequiredParamsNotProvidedException

        song_id = request.query_params.get('song_id')
        start_time = float(request.query_params.get('start_time'))
        stop_time = float(request.query_params.get('stop_time'))


        file_path = self.get_song_file_path(song_id)
        new_note_sequence = create_song_prototype(file_path, start_time, stop_time)
        prepared_song = note_sequence_to_note_list(new_note_sequence)

        return Response(prepared_song, status=status.HTTP_200_OK)

    @staticmethod
    def get_song_file_path(song_id):
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            raise SongDoesNotExistsException

        file_path = '%s/%s' % (MEDIA_ROOT, song.file.name)

        return file_path


def note_sequence_to_note_list(note_sequence):
    note = lambda note: {
        'pitch': note.pitch,
        'velocity': note.velocity,
        'start_time': note.start_time,  # round(note.start_time, 2),
        'end_time': note.end_time       # round(note.end_time, 2)
    }
    result = {
        'qpm': note_sequence.tempos[0].qpm,
        'total_time': note_sequence.total_time,
        'notes': [note(note_seq) for note_seq in note_sequence.notes]
    }
    return result


def create_song_prototype(song_path, start_time, stop_time, model_used='attention_rnn', temperature=1.0):
    magenta_model_path = '%s/magenta_models/%s.mag' % (MEDIA_ROOT, model_used)
    bundle = mm.sequence_generator_bundle.read_bundle_file(magenta_model_path)
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    melody_rnn = generator_map[model_used](checkpoint=None, bundle=bundle)
    melody_rnn.initialize()

    base_sequence = midi_file_to_note_sequence(song_path)
    target_sequence = extract_subsequence(base_sequence, start_time, stop_time)

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generator_options.generate_sections.add(
        start_time=target_sequence.total_time,
        end_time=2 * target_sequence.total_time
    )
    generated_sequence = melody_rnn.generate(target_sequence, generator_options)

    proceed_sequence = extract_subsequence(generated_sequence, target_sequence.total_time, 2*target_sequence.total_time)

    return proceed_sequence

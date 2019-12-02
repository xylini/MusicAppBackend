from rest_framework.exceptions import APIException


class SongDoesNotExistsException(APIException):
    status_code = 400
    default_detail = 'Song you are trying to get does not exists'
    default_code = 'song_not_exists'

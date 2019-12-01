from rest_framework.exceptions import APIException


class UserNameOrEmailExistsException(APIException):
    status_code = 400
    default_detail = 'Provided username or email already exists'
    default_code = 'user_already_exists'

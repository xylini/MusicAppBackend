from rest_framework.exceptions import APIException


class RequiredDataNotProvidedException(APIException):
    status_code = 400
    default_detail = 'Provided data does not match requirements'
    default_code = 'wrong_data'
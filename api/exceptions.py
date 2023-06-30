from rest_framework import exceptions, status


class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Object with this data already exists."
    default_code = "conflict"


class NotAcceptableError(exceptions.APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "No object with this data exists."
    default_code = "not acceptable"

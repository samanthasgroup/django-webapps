from rest_framework import exceptions, status


class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Object with this data already exists."
    default_code = "conflict"


class UnproccessableEntityError(exceptions.APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Failed to process input data."
    default_code = "unprocessable content"


class NotAcceptableError(exceptions.APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "No object with this data exists."
    default_code = "not acceptable"

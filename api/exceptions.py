from rest_framework import exceptions, status


class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Object with this data already exists."
    default_code = "conflict"

from collections.abc import Callable

from django.http import HttpRequest, JsonResponse
from rest_framework import status
from rest_framework.response import Response

from api.exceptions import NotAcceptableError


class CustomStatusCodeMiddleware:
    """Middleware that returns code 406 if no records with given params were found on GET request.

    The default DRF behavior would be to return an empty list with status code 200 OK.
    """

    def __init__(self, get_response: Callable[[HttpRequest], Response]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> Response | JsonResponse:
        response: Response = self.get_response(request)

        if request.method != "GET":
            return response

        if not response.data:
            return JsonResponse(
                {"detail": NotAcceptableError.default_detail},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        return response

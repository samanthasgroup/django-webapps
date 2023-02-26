from http import HTTPStatus

from rest_framework.response import Response
from rest_framework.views import APIView

from api.share.requests import InvalidRequestObject
from api.share.requests.users import GetUsersCountRequest
from api.share.responses import ResponseFailure
from api.share.tools import build_correct_http_response
from api.use_cases.get_users_count import UsersCount


class UserCountView(APIView):
    def get(self, request):
        params = request.query_params
        # object contains correct parameters
        request_object = GetUsersCountRequest.from_dict(params)
        # if something went wrong
        if isinstance(request_object, InvalidRequestObject):
            return Response(
                build_correct_http_response(
                    data={},
                    current_url=request.build_absolute_uri(),
                    status=HTTPStatus.BAD_REQUEST,
                    errors=request_object.errors,
                )
            )
        use_case = UsersCount()  # init use case object
        # call use case method with the object contains correct parameters
        use_case_response = use_case.execute(request_object)
        # if something went wrong in business logic
        if isinstance(use_case_response, ResponseFailure):
            return Response(
                build_correct_http_response(
                    data={},
                    current_url=request.build_absolute_uri(),
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                    errors=use_case_response.errors,
                )
            )

        return Response(
            # build correct formatting response
            build_correct_http_response(
                data={"count": use_case_response.value},
                current_url=request.build_absolute_uri(),
                status=HTTPStatus.OK,
            )
        )

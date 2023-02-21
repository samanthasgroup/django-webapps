from api.share.tools import build_correct_http_response
from api.share.requests.users import GetUsersCountRequest
from api.share.requests import InvalidRequestObject
from api.use_cases.get_users_count import UsersCount
from rest_framework.views import APIView
from rest_framework.response import Response
from http import HTTPStatus


class UserCountView(APIView):

    def get(self, request):
        try:
            params = request.query_params
            request_object = GetUsersCountRequest.from_dict(params) # object contains correct parameters
            # if something went wrong
            if isinstance(request_object, InvalidRequestObject):
                return Response(
                    build_correct_http_response(
                        data={},
                        current_url=request.build_absolute_uri(),
                        status=HTTPStatus.BAD_REQUEST,
                        errors=request_object.errors
                    )
                )
            use_case = UsersCount() # init use case object
            # call use case method with the object contains correct parameters
            use_case_response = use_case.execute(request_object)
            return Response(
                # build correct formatting response
                build_correct_http_response(
                    data={"count": use_case_response.value},
                    current_url=request.build_absolute_uri(),
                    status=HTTPStatus.OK
                )
            )
        except Exception as exc:
            return Response(
                build_correct_http_response(
                    data={},
                    current_url=request.build_absolute_uri(),
                    status=HTTPStatus.BAD_REQUEST,
                    errors=[{"no parameter": str(exc)}])
                )

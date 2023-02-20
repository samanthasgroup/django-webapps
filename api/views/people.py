from api.share.tools import build_correct_http_response
from api.share.requests.users import GetUsersCountRequest
from api.use_cases.get_users_count import UsersCount
from rest_framework.views import APIView
from rest_framework.response import Response
from http import HTTPStatus
from rest_framework import status
from rest_framework import permissions

# TODO Exceptions handling
class UserCountView(APIView):

    def get(self, request):
        params = request.query_params
        request_object = GetUsersCountRequest.from_dict(params) # object contains correct parameters
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


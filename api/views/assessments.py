from http import HTTPStatus

from rest_framework.response import Response
from rest_framework.views import APIView

from api.share.requests import InvalidRequestObject
from api.share.requests.assessment_tests import GetAssessmentTestsRequest
from api.share.responses import ResponseFailure
from api.share.tools import build_correct_http_response
from api.use_cases.get_assessment_tests import AssessmentTest


class AssessmentTestView(APIView):
    def get(self, request):
        params = request.query_params
        # object contains correct parameters
        request_object = GetAssessmentTestsRequest.from_dict(params)
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

        assessment_test = AssessmentTest()  # init use case object
        # call use case method with the object contains correct parameters
        assessment_test_response = assessment_test.execute(request_object)
        # if something went wrong in business logic
        if isinstance(assessment_test_response, ResponseFailure):
            return Response(
                build_correct_http_response(
                    data={},
                    current_url=request.build_absolute_uri(),
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                    errors=assessment_test_response.errors,
                )
            )
        try:
            current_page = int(params.get("page", 1))
        except ValueError:
            current_page = 1

        return Response(
            # build correct formatting response
            build_correct_http_response(
                data=assessment_test_response.value,
                current_url=request.build_absolute_uri(),
                status=HTTPStatus.OK,
                current_page=current_page,
            )
        )

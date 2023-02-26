from api.models.enrollment_test import EnrollmentTest
from api.serializers.enrollments_serializers import (
    EnrollmentTestQuestionOptionSerializer,
    EnrollmentTestQuestionSerializer,
    EnrollmentTestSerializer,
)
from api.share.requests.assessment_tests import GetAssessmentTestsRequest
from api.use_cases import UseCase


class AssessmentTest(UseCase):
    def __int__(self):
        pass

    def process_request(self, request_object: GetAssessmentTestsRequest):
        # business logic
        language = request_object.language
        level = request_object.level

        tests = EnrollmentTest.objects
        if language:
            tests = tests.filter(language__name_internal__iexact=language)
        if level:
            tests = tests.filter(levels__name__iexact=level)

        response = EnrollmentTestSerializer(tests, many=True).data

        for id1, test in enumerate(tests):
            questions = test.enrollmenttestquestion_set.all()
            response[id1]["questions"] = EnrollmentTestQuestionSerializer(
                questions, many=True
            ).data

            for id2, question in enumerate(questions):
                answers = question.enrollmenttestquestionoption_set.all()
                response[id1]["questions"][id2][
                    "options"
                ] = EnrollmentTestQuestionOptionSerializer(answers, many=True).data

        return response

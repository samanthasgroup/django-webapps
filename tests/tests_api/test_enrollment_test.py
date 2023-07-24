import pytest
from model_bakery import baker
from rest_framework import status

from api.models import EnrollmentTest, EnrollmentTestQuestionOption, Student
from api.serializers import EnrollmentTestSerializer
from tests.tests_api.asserts import assert_response_data_list


def test_get_enrollment_test(api_client):
    """Test passing enrollment test."""
    test = baker.make(EnrollmentTest, make_m2m=True)
    response = api_client.get(f"/api/enrollment_test/?language={test.language.id}")
    assert response.status_code == status.HTTP_200_OK
    assert_response_data_list(response.data, [EnrollmentTestSerializer(test).data])


@pytest.mark.parametrize(
    "number_of_questions, total_answers, correct_answers, expected_level",
    [
        (35, 35, 35, "C1"),
        (35, 35, 32, "C1"),
        (35, 35, 31, "B2"),
        (35, 35, 27, "B2"),
        (35, 35, 26, "B1"),
        (35, 35, 20, "B1"),
        (35, 35, 19, "A2"),
        (35, 35, 13, "A2"),
        (35, 35, 12, "A1"),
        (35, 35, 6, "A1"),
        (35, 35, 5, "A0"),
        (35, 35, 0, "A0"),
        (25, 25, 25, "B1"),
        (25, 25, 19, "B1"),
        (25, 25, 18, "A2"),
        (25, 25, 11, "A2"),
        (25, 25, 10, "A1"),
        (25, 25, 5, "A1"),
        (25, 25, 4, "A0"),
        (25, 25, 0, "A0"),
        # Imitating the user cancelling the test prematurely - fewer answers than questions:
        (35, 33, 32, "C1"),
        (35, 32, 31, "B2"),
        (35, 28, 27, "B2"),
        (35, 27, 26, "B1"),
        (35, 21, 20, "B1"),
        (35, 20, 19, "A2"),
        (35, 14, 13, "A2"),
        (35, 13, 12, "A1"),
        (35, 7, 6, "A1"),
        (35, 6, 5, "A0"),
        (35, 5, 0, "A0"),
        (25, 20, 19, "B1"),
        (25, 19, 18, "A2"),
        (25, 12, 11, "A2"),
        (25, 11, 10, "A1"),
        (25, 6, 5, "A1"),
        (25, 5, 4, "A0"),
        (25, 5, 0, "A0"),
    ],
)
def test_get_level(
    api_client, number_of_questions, total_answers, correct_answers, expected_level
):
    """Test calculating the resulting level of enrollment test."""
    # Don't need to specify a test here, just take some correct and incorrect answers to any test
    correct_answers_ids = list(
        EnrollmentTestQuestionOption.objects.filter(is_correct=True).values_list("id", flat=True)
    )[:correct_answers]

    incorrect_answers_ids = list(
        EnrollmentTestQuestionOption.objects.filter(is_correct=False).values_list("id", flat=True)
    )[: total_answers - correct_answers]

    response = api_client.post(
        "/api/enrollment_test_result/get_level/",
        data={
            "answers": correct_answers_ids + incorrect_answers_ids,
            "number_of_questions": number_of_questions,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "resulting_level": expected_level,
    }


def test_get_level_raises_400_with_wrong_number_of_questions(api_client):
    test = baker.make_recipe("tests.enrollment_test")
    correct_answers_ids = list(
        EnrollmentTestQuestionOption.objects.filter(
            question__enrollment_test=test, is_correct=True
        ).values_list("id", flat=True)
    )
    response = api_client.post(
        "/api/enrollment_test_result/get_level/",
        data={"answers": correct_answers_ids, "number_of_questions": len(correct_answers_ids) - 1},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "non_field_errors": ["Enrollment test with 34 questions is not supported"]
    }


def test_create_student_enrollment_test_result(api_client, availability_slots):
    """Test passing enrollment test."""
    test = baker.make_recipe("tests.enrollment_test")
    correct_answers_ids = list(
        EnrollmentTestQuestionOption.objects.filter(
            question__enrollment_test=test, is_correct=True
        ).values_list("id", flat=True)
    )
    student = baker.make(Student, make_m2m=True, availability_slots=availability_slots)
    response = api_client.post(
        "/api/enrollment_test_result/",
        data={
            "student": student.personal_info.id,
            "enrollment_test": test.id,
            "answers": correct_answers_ids,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "student": student.personal_info.id,
        "answers": correct_answers_ids,
    }

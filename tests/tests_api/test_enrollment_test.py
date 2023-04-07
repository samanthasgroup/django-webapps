from model_bakery import baker
from rest_framework import status

from api.models import EnrollmentTest, EnrollmentTestQuestionOption, Student


def test_get_enrollment_test(api_client):
    """Test passing enrollment test."""
    test = baker.make(EnrollmentTest, make_m2m=True)
    response = api_client.get(f"/api/enrollment_test/?language={test.language.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": test.id,
            "language": test.language.id,
            "age_ranges": [age_range.id for age_range in test.age_ranges.all()],
            "questions": [
                {
                    "id": question.id,
                    "text": question.text,
                    "options": [
                        {
                            "id": option.id,
                            "text": option.text,
                        }
                        for option in question.options.all()
                    ],
                }
                for question in test.questions.all()
            ],
        }
    ]


def test_create_student_enrollment_test_result(api_client):
    """Test passing enrollment test."""
    test = baker.make_recipe("tests.enrollment_test")
    correct_answers_ids = list(
        EnrollmentTestQuestionOption.objects.filter(
            question__enrollment_test=test, is_correct=True
        ).values_list("id", flat=True)
    )
    student = baker.make(Student, make_m2m=True)
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
        "is_passed": True,
        "right_answers_percentage": 100,
    }

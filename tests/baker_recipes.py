from model_bakery.recipe import Recipe, related

from api.models import EnrollmentTest, EnrollmentTestQuestion, EnrollmentTestQuestionOption

QUESTIONS_AMOUNT = 4

questions_options = [
    Recipe(EnrollmentTestQuestionOption, text="Option 1"),
    Recipe(EnrollmentTestQuestionOption, text="Option 2"),
    Recipe(EnrollmentTestQuestionOption, text="Option 3"),
    Recipe(EnrollmentTestQuestionOption, text="Option 4", is_correct=True),
]

question = Recipe(EnrollmentTestQuestion, options=related(*questions_options))

questions = [
    Recipe(EnrollmentTestQuestion, text=f"Question {i}", options=related(*questions_options))
    for i in range(1, QUESTIONS_AMOUNT + 1)
]

enrollment_test = Recipe(
    EnrollmentTest,
    questions=related(*questions),
)

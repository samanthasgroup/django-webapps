from model_bakery.recipe import Recipe, related

from api.models import EnrollmentTest, EnrollmentTestQuestion, EnrollmentTestQuestionOption

QUESTIONS_AMOUNT = 35

questions_options = [
    Recipe(EnrollmentTestQuestionOption, text="Option 1", is_correct=False),
    Recipe(EnrollmentTestQuestionOption, text="Option 2", is_correct=False),
    Recipe(EnrollmentTestQuestionOption, text="Option 3", is_correct=False),
    Recipe(EnrollmentTestQuestionOption, text="Option 4", is_correct=True),
]

questions = [
    Recipe(EnrollmentTestQuestion, text=f"Question {i}", options=related(*questions_options))
    for i in range(1, QUESTIONS_AMOUNT + 1)
]

enrollment_test = Recipe(
    EnrollmentTest,
    questions=related(*questions),
)

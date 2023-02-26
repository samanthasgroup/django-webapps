from django.urls import path

from api.views import assessments, people

urlpatterns = [
    path("users/count/", people.UserCountView.as_view()),
    path("assessments/", assessments.AssessmentTestView.as_view()),
]

from django.urls import path
from api.views import people, assessments

urlpatterns = [
    path('users/count/', people.UserCountView.as_view()),
    path('assessments/', assessments.AssessmentTestView.as_view()),
]
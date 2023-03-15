from django.urls import path

from api.views.people import StudentList

urlpatterns = [
    path("students/", StudentList.as_view()),
    #   path('students/<uuid>/', StudentDetail().get_object)
]

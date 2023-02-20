from django.urls import path
from api.views import people

urlpatterns = [
    path('users/count/', people.UserCountView.as_view()),
]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PersonalInfoViewSet

router = DefaultRouter()
router.register(r'personal_info', PersonalInfoViewSet,basename="personal_info")

urlpatterns = [
    path('', include(router.urls)),
]

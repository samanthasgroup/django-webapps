from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("api/", include("api.urls")),
    path("docs/yaml-schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("select2/", include("django_select2.urls")),
    path("", admin.site.urls),
]

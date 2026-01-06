from typing import Any

from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest

from api.models import Coordinator


class CoordinatorRestrictedAdminMixin(ModelAdmin[Any]):
    """Mixin for restricting access to coordinators to data."""

    def get_coordinator(self, request: HttpRequest) -> Coordinator | None:
        if request.user.is_authenticated and request.user.groups.filter(name="Координатор").exists():
            try:
                return Coordinator.objects.get(user=request.user)
            except Coordinator.DoesNotExist:
                return None
        return None

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        coordinator = self.get_coordinator(request)
        if coordinator:
            qs = self.filter_for_coordinator(qs, coordinator)
        return qs

    def filter_for_coordinator(self, _qs: QuerySet[Any], _coordinator: Coordinator) -> QuerySet[Any]:
        """Method for filtering QuerySet. Implemented in child classes."""
        raise NotImplementedError

from django.contrib import admin

from api.models.role import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin[Role]):
    list_display = ("name", "slug")
    search_fields = ("name",)

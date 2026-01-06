from typing import Any

from django.core.management.base import BaseCommand

from api.models.role import Role


class Command(BaseCommand):
    help = "Creates the default teacher roles if they do not exist."

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002
        roles = [
            {"name": "Методист", "slug": "methodist"},
            {"name": "Ведущий разговорного клуба", "slug": "speaking-club-leader"},
        ]

        for role_data in roles:
            role, created = Role.objects.get_or_create(slug=role_data["slug"], defaults={"name": role_data["name"]})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created role: {role.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Role already exists: {role.name}"))

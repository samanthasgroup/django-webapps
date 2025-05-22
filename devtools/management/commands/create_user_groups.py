from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = "Initialize groups and permissions"

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002
        groups_config = {
            "Админ": {
                "api": [
                    # Права для учителей
                    "view_teacher",
                    "add_teacher",
                    "change_teacher",
                    "delete_teacher",
                    # Права для учеников
                    "view_student",
                    "add_student",
                    "change_student",
                    "delete_student",
                    # Права для координаторов (без удаления)
                    "view_coordinator",
                    "add_coordinator",
                    "change_coordinator",
                    # Другие модели...
                    "view_alert",
                    "add_alert",
                    "change_alert",
                    "delete_alert",
                    "view_agerange",
                    "add_agerange",
                    "change_agerange",
                    "delete_agerange",
                    "view_dayandtimeslot",
                    "add_dayandtimeslot",
                    "change_dayandtimeslot",
                    "delete_dayandtimeslot",
                    "view_enrollmenttest",
                    "add_enrollmenttest",
                    "change_enrollmenttest",
                    "delete_enrollmenttest",
                    "view_enrollmenttestquestion",
                    "add_enrollmenttestquestion",
                    "change_enrollmenttestquestion",
                    "delete_enrollmenttestquestion",
                    "view_enrollmenttestquestionoption",
                    "add_enrollmenttestquestionoption",
                    "change_enrollmenttestquestionoption",
                    "delete_enrollmenttestquestionoption",
                    "view_enrollmenttestresult",
                    "add_enrollmenttestresult",
                    "change_enrollmenttestresult",
                    "delete_enrollmenttestresult",
                    "view_group",
                    "add_group",
                    "change_group",
                    "delete_group",
                    "view_grouplogevent",
                    "add_grouplogevent",
                    "change_grouplogevent",
                    "delete_grouplogevent",
                    "view_language",
                    "add_language",
                    "change_language",
                    "delete_language",
                    "view_languageandlevel",
                    "add_languageandlevel",
                    "change_languageandlevel",
                    "delete_languageandlevel",
                    "view_languagelevel",
                    "add_languagelevel",
                    "change_languagelevelElm",
                    "delete_languagelevel",
                    "view_nonteachinghelp",
                    "add_nonteachinghelp",
                    "change_nonteachinghelp",
                    "delete_nonteachinghelp",
                    "view_personalinfo",
                    "add_personalinfo",
                    "change_personalinfo",
                    "delete_personalinfo",
                    "view_speakingclub",
                    "add_speakingclub",
                    "change_speakingclub",
                    "delete_speakingclub",
                    "view_studentlogevent",
                    "add_studentlogevent",
                    "change_studentlogevent",
                    "delete_studentlogevent",
                    "view_teacherlogevent",
                    "add_teacherlogevent",
                    "change_teacherlogevent",
                    "delete_teacherlogevent",
                    "view_teacherunder18",
                    "add_teacherunder18",
                    "change_teacherunder18",
                    "delete_teacherunder18",
                    "view_teacherunder18logevent",
                    "add_teacherunder18logevent",
                    "change_teacherunder18logevent",
                    "delete_teacherunder18logevent",
                    "view_timeslot",
                    "add_timeslot",
                    "change_timeslot",
                    "delete_timeslot",
                ],
                #  Отдлеьный блок, для прав из других приложений, тут для примера
                # "auth": ["view_group", "add_group", "change_group", "delete_group"],
            },
            "Координатор": {
                "api": [
                    # Просмотр и изменение своих групп, учеников, учителей
                    "view_student",
                    "add_student",
                    "change_student",
                    "view_teacher",
                    "change_teacher",
                    "view_teacherunder18",
                    "change_teacherunder18",
                    "view_group",
                    "add_group",
                    "change_group",
                    # Просмотр логов
                    "view_grouplogevent",
                    "view_studentlogevent",
                    "view_teacherlogevent",
                    "view_teacherunder18logevent",
                    # Просмотр расписания и уровней
                    "view_dayandtimeslot",
                    "view_timeslot",
                    "view_languageandlevel",
                    "view_languagelevel",
                ],
            },
        }

        # Создание групп и назначение прав
        for group_name, apps_permissions in groups_config.items():
            # Создаем или получаем группу
            group, created = Group.objects.get_or_create(name=group_name)
            status = "created" if created else "already exists"
            self.stdout.write(self.style.SUCCESS(f"Group {group_name} {status}"))

            # Собираем все разрешения для группы
            permission_filters = Q()

            # Для каждого приложения создаем свой фильтр
            for app_label, codenames in apps_permissions.items():
                if codenames:
                    permission_filters |= Q(
                        content_type__app_label=app_label, codename__in=codenames
                    )

            # Получаем все разрешения по созданному фильтру
            if permission_filters:
                permissions = Permission.objects.filter(permission_filters)

                # Проверяем, все ли права найдены
                expected_count = sum(len(codenames) for codenames in apps_permissions.values())
                found_count = permissions.count()

                if found_count != expected_count:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Warning for {group_name}: Expected {expected_count} permissions, found {found_count}."
                        )
                    )

                # Назначаем права группе
                group.permissions.set(permissions)
                self.stdout.write(
                    self.style.SUCCESS(f"Assigned {found_count} permissions to {group_name}")
                )
            else:
                group.permissions.clear()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"No permissions specified for {group_name}, cleared existing."
                    )
                )

        self.stdout.write(self.style.SUCCESS("Groups and permissions initialized successfully"))

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")
django.setup()

from api.algorithms.group_manager import GroupManager  # noqa: E402

if __name__ == "__main__":
    for teacher in GroupManager.get_available_teachers():
        group = GroupManager.create_group(teacher.personal_info.pk)

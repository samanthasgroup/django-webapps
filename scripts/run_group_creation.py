import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")
django.setup()

from api.processors.auxil.algorithms import GroupBuilderAlgorithm  # noqa: E402

if __name__ == "__main__":
    for teacher in GroupBuilderAlgorithm.get_available_teachers():
        group = GroupBuilderAlgorithm.create_and_save_group(teacher.personal_info.pk)

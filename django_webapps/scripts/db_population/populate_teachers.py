import argparse
import csv

COLUMN_NAME_TO_INDEX = {
    "tid": 0,
    "cid": 1,
    "status": 3,
    "name": 4,
    "email": 5,
    "tg": 6,
    "timezone": 7,
    "experience": 8,
    "groups_number": 12,
    "age_ranges": 13,
    "language_levels": 14,
    "mon": 15,
    "tue": 16,
    "wed": 17,
    "thu": 18,
    "fri": 19,
    "sat": 20,
    "sun": 21,
    "speaking_club": 22,
    "can_give_feedback": 23,
    "other_help_comment": 24,
}


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", "-i", required=True, help="Input csv file with teachers")
    return parser.parse_args()


def load_teachers(path_to_csv_file: str) -> list[list[str]]:
    with open(path_to_csv_file, newline="") as csvfile:  # noqa: PTH123
        return list(csv.reader(csvfile))


class TeacherPopulator:
    def run(self) -> None:
        pass

    def _create_teacher(self) -> None:
        pass

    def _create_personal_info(self) -> None:
        pass

    def _create_language_and_levels(self) -> None:
        pass

    def _create_availability_slots(self) -> None:
        pass

    def _create_comment(self) -> None:
        pass


if __name__ == "__main__":
    args = get_args()
    teachers = load_teachers(args.input_csv)

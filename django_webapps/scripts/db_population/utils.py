import argparse
import csv
import logging


def get_logger(file_name: str) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(file_name)
    file_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(file_handler)
    return logger


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_csv", "-i", type=str, required=True, help="Input csv file with teachers"
    )
    parser.add_argument(
        "--dry",
        "-d",
        type=bool,
        help="dry mode, prevent from inserting data into the database",
        default=False,
    )
    return parser.parse_args()


def load_csv_data(path_to_csv_file: str) -> list[list[str]]:
    with open(path_to_csv_file, newline="") as csvfile:  # noqa: PTH123
        return list(csv.reader(csvfile))

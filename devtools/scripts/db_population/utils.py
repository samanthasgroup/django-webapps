import argparse
import csv
import json
import logging
from typing import Any


def get_logger(file_name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    file_handler = logging.FileHandler(file_name)
    file_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    return logger


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_csv",
        "-i",
        type=str,
        required=True,
        help="Input csv file with data (coordinators, teachers or students)",
    )
    parser.add_argument(
        "--dry",
        "-d",
        type=bool,
        help="dry mode, prevent from inserting data into the database",
        default=False,
    )
    return parser


def get_args() -> argparse.Namespace:
    parser = get_parser()
    return parser.parse_args()


def load_csv_data(path_to_csv_file: str) -> list[list[str]]:
    with open(path_to_csv_file, newline="") as csvfile:  # noqa: PTH123
        return list(csv.reader(csvfile))


def load_json_data(path_to_csv_file: str) -> dict[Any, Any]:
    with open(path_to_csv_file, newline="", encoding="UTF-8") as jsonfile:  # noqa: PTH123
        return json.load(jsonfile)

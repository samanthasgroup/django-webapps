from http import HTTPStatus
from math import ceil
from typing import Union


def build_correct_http_response(
    data: Union[dict, list[dict]],
    current_url: str,
    status: HTTPStatus,
    errors: list[dict[str:str]] = None,
    pagination_count_per_page: int = 10,
    current_page: int = 1,
) -> dict:
    http_response = {
        "_metadata": {
            "statusCode": status.value,
            "messages": errors if errors else {"status": status.phrase},
        },
        "_links": {"self": current_url},
    }

    if isinstance(data, dict):
        http_response["data"] = data
        # Evaluate collection url
        # current_url = https://test.com/api/v1/users/count/?registration_bot_chat_id=1234567890
        # http_response["_links"]["collection"] = https://test.com/api/v1/users
        http_response["_links"]["collection"] = "/".join(current_url.split("/")[:-2])
    elif isinstance(data, list):
        from_ = (current_page - 1) * pagination_count_per_page
        to_ = current_page * pagination_count_per_page
        http_response["data"] = data[from_:to_]

        total_elements = len(data)
        total_pages = ceil(total_elements / pagination_count_per_page)
        pagination = {
            "page": current_page,
            "totalPages": total_pages,
            "totalElements": total_elements,
            "size": pagination_count_per_page,
            "offset": (current_page - 1) * pagination_count_per_page,
        }
        http_response["_metadata"]["pagination"] = pagination

        current_url_split = current_url.split("&")
        current_url_wo_page = "&".join([part for part in current_url_split if "page" not in part])

        if current_page <= 1:
            http_response["_links"]["previous"] = ""
        else:
            http_response["_links"]["previous"] = (
                current_url_wo_page
                + ("&" if "?" in current_url_wo_page else "?")
                + f"page={(current_page - 1)}"
            )

        if current_page >= total_pages:
            http_response["_links"]["next"] = ""
        else:
            http_response["_links"]["next"] = (
                current_url_wo_page
                + ("&" if "?" in current_url_wo_page else "?")
                + f"page={(current_page + 1)}"
            )
    else:
        http_response["_metadata"] = {
            "data": {},
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "messages": [{"no parameters": "Data must be dict or list"}],
        }

    return http_response

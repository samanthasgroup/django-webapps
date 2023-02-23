from math import ceil
from typing import Dict, List, Union
from http import HTTPStatus


def build_correct_http_response(data: Union[Dict, List],
                                current_url: str,
                                status: HTTPStatus,
                                errors: List = None,
                                pagination_count_per_page: int = 10,
                                current_page: int = 1
                                ) -> Dict:
    http_response = {
        "_metadata": {
            "statusCode": status.value,
            "messages": errors if errors else {"status": status.phrase}
        },
        "_links": {
            "self": current_url
        }
    }

    if isinstance(data, dict):
        http_response["data"] = data
        http_response["_links"]["collection"] = "/".join(current_url.split("/")[:-2])
    elif isinstance(data, list):
        from_ = (current_page-1)*pagination_count_per_page
        to_ = current_page*pagination_count_per_page
        http_response["data"] = data[from_:to_]

        total_elements = len(data)
        total_pages = ceil(total_elements/pagination_count_per_page)
        pagination = {
            "page": current_page,
            "totalPages": total_pages,
            "totalElements": total_elements,
            "size": pagination_count_per_page,
            "offset": (current_page-1)*pagination_count_per_page
        }
        http_response["_metadata"]["pagination"] = pagination

        current_url_split = current_url.split("&")
        current_url_wo_page = "&".join([part for part in current_url_split if "page" not in part])

        if current_page <= 1:
            http_response["_links"]["previous"] = ""
        else:
            http_response["_links"]["previous"] = current_url_wo_page + \
                                                  ('&' if '?' in current_url_wo_page else '?') + \
                                                  f"page={(current_page - 1)}"

        if current_page >= total_pages:
            http_response["_links"]["next"] = ""
        else:
            http_response["_links"]["next"] = current_url_wo_page + \
                                              ('&' if '?' in current_url_wo_page else '?') + \
                                              f"page={(current_page + 1)}"

    else:
        raise ValueError("data must be dict or list")

    return http_response

from typing import Dict, List, Union
from http import HTTPStatus


def build_correct_http_response(data: Union[Dict, List],
                                current_url: str,
                                status: HTTPStatus,
                                errors: List = None
                                ) -> Dict:
    http_response = {
        "data": data,
        "_metadata": {
            "statusCode": status.value,
            "messages": errors if errors else {"status": status.phrase}
        },
        "_links": {
            "self": current_url
        }
    }

    if isinstance(data, dict):
        http_response["_links"]["collection"] = "/".join(current_url.split("/")[:-2])
    elif isinstance(data, list):
        pass
    else:
        raise ValueError("data must be dict or list")

    return http_response
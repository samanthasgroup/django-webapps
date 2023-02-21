import re
from api.share.requests import ValidRequestObject, InvalidRequestObject


class GetUsersCountRequest(ValidRequestObject):

    def __init__(self,
                 registration_bot_chat_id: str,
                 tg_username: str,
                 phone: str,
                 email: str,
                 first_name: str,
                 last_name: str):
        self.registration_bot_chat_id = registration_bot_chat_id
        self.tg_username = tg_username
        self.phone = phone
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def from_dict(cls, input_dict):
        # Check input parameters.
        invalid_request = InvalidRequestObject()
        # https://core.telegram.org/bots/api#chat : chat_id - max 52 significant bits
        # 9007199254740991 is the max number you can store in the 53 bits => len(chat_id) <= 16
        if input_dict.get("registration_bot_chat_id") and \
                len(input_dict.get("registration_bot_chat_id")) > 16:
            invalid_request.add_error("registration_bot_chat_id", "Invalid length")

        if input_dict.get("tg_username") and (len(input_dict.get("tg_username")) < 5 or
                                              len(input_dict.get("tg_username")) > 32):
            invalid_request.add_error("tg_username", "Invalid length")

        # See modal PersonalInfo
        if input_dict.get("first_name") and len(input_dict.get("first_name")) > 100:
            invalid_request.add_error("first_name", "Invalid length")

        # See modal PersonalInfo
        if input_dict.get("last_name") and len(input_dict.get("last_name")) > 100:
            invalid_request.add_error("last_name", "Invalid length")

        if input_dict.get("email") and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', input_dict.get("email")):
            invalid_request.add_error("email", "Incorrect format")

        if input_dict.get("email") and len(input_dict.get("email")) > 100:
            invalid_request.add_error("email", "Invalid length")

        # Phone must start with + or 00
        if input_dict.get("phone") and not re.match(r'^\+|00', input_dict.get("phone")):
            invalid_request.add_error("phone", "Incorrect format")

        if input_dict.get("phone") and len(input_dict.get("phone")) > 12:
            invalid_request.add_error("phone", "Invalid length")

        if invalid_request.has_errors():
            return invalid_request

        return cls(registration_bot_chat_id=input_dict.get("registration_bot_chat_id"),
                   tg_username=input_dict.get("tg_username"),
                   phone=input_dict.get("phone"),
                   email=input_dict.get("email"),
                   first_name=input_dict.get("first_name"),
                   last_name=input_dict.get("last_name")
                   )

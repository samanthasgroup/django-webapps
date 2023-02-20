from api.share.requests import ValidRequestObject


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
        # TODO
        # Check input parameters.
        return cls(registration_bot_chat_id=input_dict.get("registration_bot_chat_id"),
                   tg_username=input_dict.get("tg_username"),
                   phone=input_dict.get("phone"),
                   email=input_dict.get("email"),
                   first_name=input_dict.get("first_name"),
                   last_name=input_dict.get("last_name")
                   )

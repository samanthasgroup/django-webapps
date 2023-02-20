from api.use_cases import UseCase
from api.share.requests.users import GetUsersCountRequest
from api.models.people import PersonalInfo
from django.db.models.functions import Lower


class UsersCount(UseCase):

    def __int__(self):
        pass

    def process_request(self, request_object: GetUsersCountRequest):
        # business logic
        registration_bot_chat_id = request_object.registration_bot_chat_id
        tg_username = request_object.tg_username
        phone = request_object.phone
        email = request_object.email
        first_name = request_object.first_name
        last_name = request_object.last_name

        res = PersonalInfo.objects
        if registration_bot_chat_id:
            res = res.filter(registration_bot_chat_id=registration_bot_chat_id)
        if tg_username:
            res = res.filter(tg_username__iexact=tg_username)
        if phone:
            res = res.filter(phone=phone)
        if email:
            res = res.filter(email__iexact=email)
        if first_name:
            res = res.filter(first_name__iexact=first_name)
        if last_name:
            res = res.filter(last_name__iexact=last_name)

        return res.count()

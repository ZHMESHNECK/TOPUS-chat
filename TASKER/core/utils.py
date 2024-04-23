from TASKER.api.schemas.users import StatusFriend, UserFToken
from TASKER.db.models import UserDB
from typing import List

# Поля які потрібно повернути
fields = ['id', 'username', 'online', 'last_seen']


# search
def get_list_user(result_user: List[UserDB], token: UserFToken):
    list_user = []
    for user in result_user:
        user_dict = user.as_dict(fields=fields)
        # Отримуємо список ідентифікаторів друзів користувача
        friend_id = []
        for friend in user.friends:
            if friend.friend_id == token.id:
                friend_id.append(token.id)
        # Перевіряємо, чи є користувач у друзях
        user_dict['is_friend'] = token.id in friend_id

        if user_dict['is_friend'] == False:

            # Перевіряємо чи надіслав користвач запит на "дружбу" нашому юзеру
            request_id = [
                user.receiver_id for user in user.sent_requests if user.status == StatusFriend.pending.value]
            if token.id in request_id:
                user_dict['reque'] = True
            else:
                user_dict['reque'] = False
        else:
            user_dict['reque'] = False

        list_user.append(user_dict)

    return list_user


# friend_request
def get_list_friend_req(result_user: List[UserDB]):
    list_user = []
    for user in result_user:
        user_dict = user.sender.as_dict(fields=fields)
        user_dict['is_friend'] = False
        user_dict['reque'] = True
        list_user.append(user_dict)
    return list_user


# messege_request
def get_list_message_req(result_user: List[UserDB], token: UserFToken):
    # список словарів з юзерами які надіслали запит на "дружбу"
    list_user = []
    for user in result_user:
        user_dict = user.sender.as_dict(fields=fields)
        # Отримуємо список ідентифікаторів друзів користувача
        friend_ids = [
            friend.friend_id for friend in user.sender.friends]
        # Перевіряємо, чи є користувач у друзях
        user_dict['is_friend'] = token.id in friend_ids

        if user_dict['is_friend']:
            user_dict['reque'] = False
        # Перевіряємо запит на додання в друзі
        else:
            friend_req = [
                request.receiver_id for request in user.sender.sent_requests if request.status == StatusFriend.pending.value]
            if token.id in friend_req:
                user_dict['reque'] = True
            else:
                user_dict['reque'] = False

        list_user.append(user_dict)
    return list_user


def send_message_json(type: str, sender: str | int, message: str):
    return {'type': type,
            'user': sender,
            'message': message}

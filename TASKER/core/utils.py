from TASKER.db.models import UserDB
from typing import Dict, List

# Поля які потрібно повернути
fields = ['id', 'username', 'online', 'last_seen']


def get_list_user(result_user: List[UserDB], token: Dict):
    list_user = []
    for user in result_user:
        user_dict = user.as_dict(fields=fields)
        # Отримуємо список ідентифікаторів друзів користувача
        friend_id = [token['id'] for friend in user.friends if friend.user_name ==
                     token['username'] or friend.friend_name == token['username']]
        # Перевіряємо, чи є користувач у друзях
        user_dict['is_friend'] = token['id'] in friend_id

        if user_dict['is_friend'] == False:

            # Перевіряємо чи надіслав користвач запит на "дружбу" нашому юзеру
            request_id = [
                user.id for user in user.sent_requests if user.status == 'pending']
            if token['id'] in request_id:
                user_dict['reque'] = True
            else:
                user_dict['reque'] = False

        list_user.append(user_dict)

    return list_user

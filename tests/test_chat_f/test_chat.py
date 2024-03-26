from fastapi.testclient import TestClient
from TASKER.core.security import decode_token
from main import topus
import pytest
from asyncio import sleep


""" Default user DB
1)
    username - TestUserDB
    password - hash_password("12345678") - func
    role - default - "user"
2)
    username - TestUserDB2
    password - hash_password("12345678") - func
    role - default - "user"

    @fixture default_friendship
3)
    username - TestUserDBFriend3  - friend with 4
    password - hash_password("12345678") - func
    role - default - "user"
4)
    username - TestUserDBFriend4  - friend with 3
    password - hash_password("12345678") - func
    role - default - "user"
"""


# @pytest.mark.skip
class TestChat:

    @pytest.mark.skip
    def test_websocket(self):
        """ 
        Перевірка websocket
        """
        client = TestClient(topus)
        with client.websocket_connect("/chat/ws") as websocket:
            data = websocket.receive_text()
            assert data == "Hello WebSocket"
            websocket.close()

    @pytest.mark.skip
    async def test_create_private_chat(self):
        """Створення приватного чату
        """
        client = TestClient(topus)
        # Авторизація юзера 1
        login1 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        user1 = client.post('/auth/login', json=login1)
        assert user1.status_code == 200

        response = client.get('/chat/start_private_chat/2')
        assert response.status_code == 200

    @pytest.mark.skip
    async def test_create_private_chat_error(self):
        """Створення приватного чату з самим собою
        """
        client = TestClient(topus)
        # Авторизація юзера 1
        login1 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        user1 = client.post('/auth/login', json=login1)
        assert user1.status_code == 200
        token = decode_token(user1.cookies.get('TOPUS'))

        response = client.get(f'/chat/start_private_chat/{token["id"]}')
        assert response.status_code == 403
        assert response.json() == 'Собі не можна написати'

    @pytest.mark.skip
    async def test_connect_private(self):
        """
        Юзер надсилає приватне повідомлення
        """
        client = TestClient(topus)
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = client.post('/auth/login', json=login)
        assert response.status_code == 200

        with client.websocket_connect('/chat/private_chat/2') as websocket:
            websocket.send_text('Hi, Private!')
            ans = websocket.receive_text()
            assert ans == 'Hi, Private!'
            websocket.close()

    @pytest.mark.skip
    async def test_connect_private_second(self):
        """
        Другий юзер підключається до приватного чату з першим
        """
        client = TestClient(topus)
        # Авторизація юзера 1
        login1 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        user1 = client.post('/auth/login', json=login1)
        assert user1.status_code == 200

        # юзер 1 надсилає повідомлення юзеру 2
        with client.websocket_connect('/chat/private_chat/2') as websocket:
            websocket.send_text('Юзер 1 пишет привет')
            ans = websocket.receive_text()
            assert ans == 'Юзер 1 пишет привет'
            websocket.close()

        # Авторизація юзера 2
        login2 = {
            "username": "TestUserDB2",
            "password": "12345678",
        }
        user2 = client.post('/auth/login', json=login2)
        assert user2.status_code == 200
        # юзер 2 надсилає повідомлення юзеру 1
        with client.websocket_connect('/chat/private_chat/1') as websocket:
            websocket.send_text('Пока')
            ans = websocket.receive_text()
            assert ans == 'Пока'
            websocket.close()

    async def test_get_chat_history(self, default_friendship):
        """ Отримання історії чату між 1 та 2 юзером
        """

        client = TestClient(topus)
        # Авторизація юзера 3
        login1 = {
            "username": "TestUserDBFriend3",
            "password": "12345678",
        }
        user1 = client.post('/auth/login', json=login1)
        assert user1.status_code == 200

        # юзер 3 надсилає повідомлення юзеру 1
        with client.websocket_connect('/chat/private_chat/1') as websocket:
            websocket.send_text('Юзер 3 пишет привет юзеру 1')
            websocket.receive_text()
            await sleep(1)
            websocket.send_text('єто тест истории')
            websocket.receive_text()

            websocket.close()

        login2 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        user2 = client.post('/auth/login', json=login2)
        assert user2.status_code == 200

        response = client.get(f'/chat/get_history_chat/3')
        assert response.status_code == 200
        response.json() == [
            {'id': 1,
             'chat_id': 1,
             'sender_id': 3,
             'message': 'Юзер 3 пишет привет юзеру 1'},
            {'id': 2,
             'chat_id': 1,
             'sender_id': 3,
             'message': 'ето тест историй'}
        ]

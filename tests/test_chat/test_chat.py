from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from fastapi import Depends, WebSocket, status, WebSocketDisconnect
from asyncio import sleep

from TASKER.api.routes.chat import private_manager
from TASKER.core.config import get_session
from TASKER.core.security import chat_id_generator
from TASKER.db.chat_db import get_history_chat, get_or_create_chat
from main import topus
import pytest


""" Default user DB
1)
    login = {
        "username" : "TestUserDB",
        "password" : "12345678" - func
    role - default - "user"
    }
2)
    login2 = {
        "username" : "TestUserDB2",
        "password" : "12345678" - func
    role - default - "user"
    }

    use @fixture default_friendship
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

    # @pytest.mark.skip
    def test_websocket(self):
        """ 
        Перевірка websocket
        """
        client = TestClient(topus)
        with client.websocket_connect("/chat/ws") as websocket:
            data = websocket.receive_text()
            assert data == "Hello WebSocket"
            websocket.close()

    # @pytest.mark.skip
    async def test_create_private_chat_error(self):
        """Створення приватного чату з самим собою
        """
        client = TestClient(topus)

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect('/chat/private_chat/1/1') as websocket:
                pass

        assert exc_info.value.code == status.WS_1007_INVALID_FRAME_PAYLOAD_DATA
        assert exc_info.value.reason == 'Собі не можна написати'

    # @pytest.mark.skip
    async def test_connect_private(self):
        """
        Юзер надсилає приватне повідомлення
        """
        client = TestClient(topus)

        with client.websocket_connect('/chat/private_chat/1/2') as websocket:
            websocket.send_text('Hi, Private!')
            ans = websocket.receive_text()
            assert ans == 'Hi, Private!'
            websocket.close()


    # @pytest.mark.skip
    async def test_connect_private_second(self):
        """
        Другий юзер підключається до приватного чату з першим
        """
        client = TestClient(topus)

        # юзер 1 надсилає повідомлення юзеру 2
        with client.websocket_connect('/chat/private_chat/1/2') as websocket:
            websocket.send_text('Юзер 1 пишет привет')
            ans = websocket.receive_text()
            assert ans == 'Юзер 1 пишет привет'
            websocket.close()

        # юзер 2 надсилає повідомлення юзеру 1
        with client.websocket_connect('/chat/private_chat/2/1') as websocket:
            websocket.send_text('Пока')
            ans = websocket.receive_text()
            assert ans == 'Пока'
            websocket.close()

    # @pytest.mark.skip
    async def test_get_chat_history(self, default_friendship):
        """ Отримання історії чату між 1 та 2 юзером
        """

        client = TestClient(topus)

        # юзер 3 надсилає повідомлення юзеру 1
        with client.websocket_connect('/chat/private_chat/3/1') as websocket:
            websocket.send_text('Юзер 3 пише привіт юзеру 1')
            websocket.receive_text()
            await sleep(1)
            websocket.send_text('це тест історії')
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
             'message': 'Юзер 3 пише привіт юзеру 1'},
            {'id': 2,
             'chat_id': 1,
             'sender_id': 3,
             'message': 'це тест історії'}
        ]

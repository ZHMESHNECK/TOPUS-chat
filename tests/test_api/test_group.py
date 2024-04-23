from TASKER.core.security import decode_token
from TASKER.api.schemas.users import UserFToken
import pytest
import httpx


""" Default user DB
1)
    id: 1
    login = {
        "username" : "TestUserDB",
        "password" : "12345678" - func
    role - default - "user"
    }
2)
    id: 2

    login2 = {
        "username" : "TestUserDB2",
        "password" : "12345678" - func
    role - default - "user"
    }

3)
    username - TestUserDBFriend3  - friend with 4
    password - hash_password("12345678") - func
    role - default - "user"
4)
    username - TestUserDBFriend4  - friend with 3
    password - hash_password("12345678") - func
    role - default - "user"


5)  # owner 1
    ChatDB(chat='test_group1')
    ChatDB(chat='test_group2')
    ChatDB(chat='test_group3')
"""


# @pytest.mark.skip
class TestGroupChat:

    # @pytest.mark.skip
    async def test_create_group(self, client: httpx.AsyncClient):
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200

        response = await client.post('/chat/create_group', json={'title': 'chat_create'})
        assert response.status_code == 201
        assert response.json()['msg'] == 'Чат створенно'

    # @pytest.mark.skip
    async def test_add_one_user(self, client: httpx.AsyncClient):
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200

        response = await client.post('/chat/add_to_group', json={
            'chat': 1,
            'users': [2]
        })

        assert response.status_code == 200
        assert response.json() == 'Юзер успішно додан в чат'

    # @pytest.mark.skip
    async def test_add_two_user(self, client: httpx.AsyncClient):
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200

        response = await client.post('/chat/add_to_group', json={
            'chat': 2,
            'users': [2, 3]
        })

        assert response.status_code == 200
        assert response.json() == 'Юзери успішно додані в чат'

    # @pytest.mark.skip
    async def test_add_self(self, client: httpx.AsyncClient):
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200

        response = await client.post('/chat/add_to_group', json={
            'chat': 1,
            'users': [1]
        })

        assert response.status_code == 200
        assert response.json() == 'Юзер успішно додан в чат'

    # @pytest.mark.skip
    async def test_kick_admin(self, client: httpx.AsyncClient):
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200

        response = await client.post('/chat/kick_f_group', json={
            'chat': 1,
            'user': 1
        })

        assert response.status_code == 403
        assert response.json() == 'Адмін не може себе видалити'

    # @pytest.mark.skip
    async def test_kick_user(self, client: httpx.AsyncClient):
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200

        response = await client.post('/chat/add_to_group', json={
            'chat': 2,
            'users': 2
        })

        response = await client.post('/chat/kick_f_group', json={
            'chat': 2,
            'user': 2
        })

        assert response.status_code == 200
        assert response.json() == 'Успішно видалено'

    # @pytest.mark.skip
    async def test_user_without_rights(self, client: httpx.AsyncClient):

        login2 = {
            "username": "TestUserDB2",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login2)
        assert response.status_code == 200

        response = await client.post('/chat/kick_f_group', json={
            'chat': 1,
            'user': 1
        })

        assert response.status_code == 403
        assert response.json() == 'Не достатньо прав'

    # @pytest.mark.skip
    async def test_delete_group_without_rights(self, client: httpx.AsyncClient):

        login2 = {
            "username": "TestUserDB2",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login2)
        assert response.status_code == 200

        response = await client.delete('/chat/delete_group/group1/1')

        assert response.status_code == 403
        assert response.json() == 'Не достатньо прав'

    # @pytest.mark.skip
    async def test_delete_group(self, client: httpx.AsyncClient):

        login2 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login2)
        assert response.status_code == 200

        response = await client.delete('/chat/delete_group/group1/1')

        assert response.status_code == 200
        assert response.json() == 'Група видалена'

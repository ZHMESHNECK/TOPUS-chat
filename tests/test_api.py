from TASKER.core.security import decode_token
import pytest
import httpx


""" Default user DB
1)
    username - TestUserDB
    password - hash_password("12345678") - func
    role - default - "user"
2)
    username - TestUserDB2
    password - hash_password("12345678") - func
    role - default - "user"
"""


# @pytest.mark.skip
class TestRegistration:

    # @pytest.mark.skip
    async def test_register_success(self, client: httpx.AsyncClient):
        data = {
            "username": "Test",
            "password": "12345678",
            "re_password": "12345678",
        }

        response = await client.post('/auth/registration', json=data)

        assert response.status_code == 201
        token = decode_token(response.json()['token'])
        assert response.json() == {
            "message": "Успішно зараєстровано", "token": response.json()['token']}
        assert token['username'] == data['username']

    # @pytest.mark.skip
    async def test_register_error(self, client: httpx.AsyncClient):
        data = {
            "username": "^sdasd",
            "password": "1234567",
            "re_password": "1234567",
        }

        response = await client.post('/auth/registration', json=data)

        assert response.status_code == 400
        assert response.json() == {
            'username': 'Нікнейм повинен бути в межах від 3 до 25 літер',
            'password': 'Пароль повинен бути не менше ніж 8 літер'
        }

    # @pytest.mark.skip
    async def test_register_error_already_exist(self, client: httpx.AsyncClient):
        data = {
            "username": "Test2",
            "password": "12345671",
            "re_password": "12345671",
        }

        response = await client.post('/auth/registration', json=data)
        assert response.status_code == 201
        response = await client.post('/auth/registration', json=data)
        assert response.status_code == 400
        assert response.json() == {'detail': 'Нікнейм зайнятий, оберіть інший'}

    # @pytest.mark.skip
    async def test_register_error_passwor_repass(self, client: httpx.AsyncClient):
        data = {
            "username": "Test2",
            "password": "12345671",
            "re_password": "12345671222",
        }

        response = await client.post('/auth/registration', json=data)
        assert response.status_code == 400
        assert response.json() == {'re_password': 'Паролі не збігаються'}


# @pytest.mark.skip
class TestLogin:

    # @pytest.mark.skip
    async def test_login_successful(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200
        assert response.json() == {"message": "Успіх",
                                   "token": response.json()['token']}

    # @pytest.mark.skip
    async def test_login_error_passw(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "error_passw",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 400
        assert response.json() == {"detail": "Невірний пароль або логін"}


# @pytest.mark.skip
class TestFriend:

    # @pytest.mark.skip
    async def test_send_req_friend(self, client: httpx.AsyncClient):

        register = {
            "username": "Test3",
            "password": "12345678",
            "re_password": "12345678",
        }
        response = await client.post('/auth/registration', json=register)
        headers = {
            'Authorization': f'Bearer {response.json()["token"]}'
        }
        response = await client.get('/user/add_friend/TestUserDB', headers=headers)

        assert response.status_code == 200
        assert response.json() == 'Надіслано'

    # @pytest.mark.skip
    async def test_send_req_friend_error(self, client: httpx.AsyncClient):

        register = {
            "username": "Test4",
            "password": "12345678",
            "re_password": "12345678",
        }
        response = await client.post('/auth/registration', json=register)
        headers = {
            'Authorization': f'Bearer {response.json()["token"]}'
        }
        response = await client.get('/user/add_friend/Teasdffd2', headers=headers)

        assert response.status_code == 400
        assert response.json() == {'detail': 'Профіль не знайдено'}

    # @pytest.mark.skip
    async def test_send_req_friend_error2(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        headers = {
            'Authorization': f'Bearer {response.json()["token"]}'
        }
        response = await client.get('/user/add_friend/TestUserDB', headers=headers)

        assert response.status_code == 400
        assert response.json() == {'detail': 'Не можна відправити собі запрос'}

    # @pytest.mark.skip

    async def test_accept_req_friend_error(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        headers = {
            'Authorization': f'Bearer {response.json()["token"]}'
        }
        response = await client.get('/user/accept_friend/TestUserDB', headers=headers)

        assert response.status_code == 500
        assert response.json() == {'detail': 'Запит не знайдено'}

    # @pytest.mark.skip
    async def test_remove_friendship(self, client: httpx.AsyncClient):
        login1 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        user1 = await client.post('/auth/login', json=login1)

        login2 = {
            "username": "TestUserDB2",
            "password": "12345678",
        }
        user2 = await client.post('/auth/login', json=login2)

        headers_user1 = {
            'Authorization': f'Bearer {user1.json()["token"]}'
        }
        headers_user2 = {
            'Authorization': f'Bearer {user2.json()["token"]}'
        }

        # Відправка запиту
        response = await client.get('/user/add_friend/TestUserDB', headers=headers_user2)
        assert response.status_code == 200
        assert response.json() == 'Надіслано'

        # Прийняття запиту
        response = await client.get('/user/accept_friend/TestUserDB2', headers=headers_user1)
        assert response.status_code == 201
        assert response.json() == 'Додано до друзів'

        # Вилучення з друзів
        response = await client.delete('/user/del_friend/TestUserDB', headers=headers_user2)
        assert response.status_code == 200
        assert response.json() == 'Видалено з друзів'

    # @pytest.mark.skip
    async def test_accept_req_friend(self, client: httpx.AsyncClient):

        login1 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        user1 = await client.post('/auth/login', json=login1)

        login2 = {
            "username": "TestUserDB2",
            "password": "12345678",
        }
        user2 = await client.post('/auth/login', json=login2)

        headers_user1 = {
            'Authorization': f'Bearer {user1.json()["token"]}'
        }
        headers_user2 = {
            'Authorization': f'Bearer {user2.json()["token"]}'
        }

        # Відправка запиту
        response = await client.get('/user/add_friend/TestUserDB', headers=headers_user2)
        assert response.status_code == 200
        assert response.json() == 'Надіслано'

        # Прийняття запиту
        response = await client.get('/user/accept_friend/TestUserDB2', headers=headers_user1)
        assert response.status_code == 201
        assert response.json() == 'Додано до друзів'

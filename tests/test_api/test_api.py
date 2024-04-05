from TASKER.core.security import decode_token
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

    @fixture defaults_friendship
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
        token = decode_token(response.cookies.get('TOPUS'))
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
        assert response.json() == 'Нікнейм зайнятий, оберіть інший'

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
        token = decode_token(response.cookies.get('TOPUS'))
        assert token['username'] == login['username']

    # @pytest.mark.skip

    async def test_login_error_passw(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "error_passw",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 400
        assert response.json() == 'Невірний пароль або логін'


# @pytest.mark.skip
class TestFriend:

    # @pytest.mark.skip
    async def test_send_req_friend(self, client: httpx.AsyncClient):

        register = {
            "username": "Test3",
            "password": "12345678",
            "re_password": "12345678",
        }
        await client.post('/auth/registration', json=register)

        response = await client.get('/user/add_friend/1')

        assert response.status_code == 200
        assert response.json() == 'Надіслано'

    # @pytest.mark.skip
    async def test_declain_request(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "12345678"
        }

        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200
        response = await client.get('/user/add_friend/2')
        assert response.status_code == 200
        login2 = {
            "username": "TestUserDB2",
            "password": "12345678"
        }
        response2 = await client.post('/auth/login', json=login2)
        assert response2.status_code == 200
        response2 = await client.get(f'/user/declain_friend/1')
        assert response2.status_code == 200
        assert response2.json() == 'Запит відхилено'

    # @pytest.mark.skip
    async def test_send_req_friend_error(self, client: httpx.AsyncClient):

        register = {
            "username": "Test4",
            "password": "12345678",
            "re_password": "12345678",
        }
        await client.post('/auth/registration', json=register)

        response = await client.get('/user/add_friend/222')

        assert response.status_code == 400
        assert response.json() == 'Профіль не знайдено'

    # @pytest.mark.skip
    async def test_send_req_friend_error2(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        await client.post('/auth/login', json=login)

        response = await client.get('/user/add_friend/1')

        assert response.status_code == 400
        assert response.json() == 'Не можна відправити собі запит'

    # @pytest.mark.skip
    async def test_accept_req_friend_error(self, client: httpx.AsyncClient):

        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        await client.post('/auth/login', json=login)

        response = await client.get('/user/accept_friend/1')

        assert response.status_code == 400
        assert response.json() == 'Не можна прийняти свій запит'

    # @pytest.mark.skip
    async def test_remove_friendship(self, client: httpx.AsyncClient):
        """
            Відправляємо -> приймаємо -> видаляємо
        """
        login1 = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        await client.post('/auth/login', json=login1)

        # Відправка запиту
        response = await client.get('/user/add_friend/2')
        assert response.status_code == 200
        assert response.json() == 'Надіслано'

        login2 = {
            "username": "TestUserDB2",
            "password": "12345678",
        }
        await client.post('/auth/login', json=login2)

        # Прийняття запиту
        response = await client.get('/user/accept_friend/1')
        assert response.status_code == 201
        assert response.json() == 'Додано до друзів'

        # Вилучення з друзів
        response = await client.delete('/user/del_friend/1')
        assert response.status_code == 200
        assert response.json() == 'Видалено з друзів'


# @pytest.mark.skip
class TestMainPage:

    async def test_get_list_friend_1_friend(self, client: httpx.AsyncClient):
        login = {
            "username": "TestUserDB",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200

        response = await client.get('/')
        assert response.status_code == 200

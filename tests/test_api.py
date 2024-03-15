from TASKER.core.security import decode_token
import pytest
import httpx


class TestRegistration:

    @pytest.mark.skip
    async def test_database_connection(self, client):
        response = await client.get('auth/check')

        assert response.status_code == 200
        assert response.json() == {'status': 'OK'}

    @pytest.mark.skip
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

    @pytest.mark.skip
    async def test_register_error(self, client: httpx.AsyncClient):
        data = {
            "username": "^sdasd",
            "password": "1234567",
            "re_password": "1234567",
        }

        response = await client.post('/auth/registration', json=data)

        assert response.status_code == 400
        assert response.json() == {
            'username': 'Нікнейм повинен бути в межах від 2 до 25 літер',
            'password': 'Пароль повинен бути не менше ніж 8 літер'
        }

    @pytest.mark.skip
    async def test_register_error_already_exist(self, client: httpx.AsyncClient):
        data = {
            "username": "Test2",
            "password": "12345671",
            "re_password": "12345671",
        }

        response = await client.post('/auth/registration', json=data)
        assert response.status_code == 200
        response = await client.post('/auth/registration', json=data)
        assert response.status_code == 400
        assert response.json() == {'detail': 'Нікнейм зайнятий, оберіть інший'}

    @pytest.mark.skip
    async def test_register_error_passwor_repass(self, client: httpx.AsyncClient):
        data = {
            "username": "Test2",
            "password": "12345671",
            "re_password": "12345671222",
        }

        response = await client.post('/auth/registration', json=data)
        assert response.status_code == 400
        assert response.json() == {'re_password': 'Паролі не збігаються'}


class TestLogin:

    # @pytest.mark.skip
    async def test_login_successful(self, client: httpx.AsyncClient):
        reg_user = {
            "username": "Test3",
            "password": "12345678",
            "re_password": "12345678",
        }
        response = await client.post('/auth/registration', json=reg_user)
        assert response.status_code == 201

        login = {
            "username": "Test3",
            "password": "12345678",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200
        assert response.json() == {"message": "Успіх",
                                   "token": response.json()['token']}

    # @pytest.mark.skip
    async def test_login_error_passw(self, client: httpx.AsyncClient):
        reg_user = {
            "username": "Test4",
            "password": "12345678",
            "re_password": "12345678",
        }
        response = await client.post('/auth/registration', json=reg_user)
        assert response.status_code == 201

        login = {
            "username": "Test4",
            "password": "12345223332",
        }
        response = await client.post('/auth/login', json=login)
        assert response.status_code == 400
        assert response.json() == {"detail": "Невірний пароль або логін"}

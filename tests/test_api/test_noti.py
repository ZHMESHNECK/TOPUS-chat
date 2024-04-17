from TASKER.core.security import decode_token
from TASKER.api.schemas.users import UserFToken
# import pytest
import httpx

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
class TestNoti:

    # @pytest.mark.skip
    async def test_get_list_friend_req_noti(self, client: httpx.AsyncClient):
        """
        Реєструемо нових юзерів та відправляємо запит на дружбу TestUserDB2
        """
        data = {
            "username": "Test5",
            "password": "12345678",
            "re_password": "12345678",
        }

        response = await client.post('/auth/registration', json=data)
        assert response.status_code == 201
        token1: UserFToken = decode_token(response.cookies['TOPUS']).id
        await client.get('/user/add_friend/2')

        data2 = {
            "username": "Test6",
            "password": "12345678",
            "re_password": "12345678",
        }

        response = await client.post('/auth/registration', json=data2)
        assert response.status_code == 201
        token2 = decode_token(response.cookies['TOPUS']).id
        await client.get('/user/add_friend/2')

        data3 = {
            "username": "Test7",
            "password": "12345678",
            "re_password": "12345678",
        }

        response = await client.post('/auth/registration', json=data3)
        assert response.status_code == 201
        token3 = decode_token(response.cookies['TOPUS']).id
        await client.get('/user/add_friend/2')

        login = {
            "username": "TestUserDB2",
            "password": "12345678"
        }

        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200
        response = await client.get('/noti/friend_req')
        assert response.status_code == 200

        response = response.json()

        assert response[0]['id'] == token3
        assert response[1]['id'] == token2
        assert response[2]['id'] == token1

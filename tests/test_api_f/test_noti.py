from TASKER.core.security import decode_token
import pytest
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
        data = {
            "username": "Test2",
            "password": "12345678",
            "re_password": "12345678",
        }

        await client.post('/auth/registration', json=data)
        await client.get('/user/add_friend/TestUserDB')

        data2 = {
            "username": "Test3",
            "password": "12345678",
            "re_password": "12345678",
        }

        await client.post('/auth/registration', json=data2)
        await client.get('/user/add_friend/TestUserDB')

        data3 = {
            "username": "Test4",
            "password": "12345678",
            "re_password": "12345678",
        }

        response = await client.post('/auth/registration', json=data3)
        assert response.status_code == 201
        await client.get('/user/add_friend/TestUserDB')

        login = {
            "username": "TestUserDB",
            "password": "12345678"
        }

        response = await client.post('/auth/login', json=login)
        assert response.status_code == 200
        response = await client.get('/noti/friend_req')
        assert response.status_code == 200

        response = response.json()
        assert response[0]['username'] == data['username']
        assert response[1]['username'] == data2['username']
        assert response[2]['username'] == data3['username']

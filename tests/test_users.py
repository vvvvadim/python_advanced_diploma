import pytest
from httpx import AsyncClient
from api.config.schemas import GetUser, ErrorMSG, MSG


class TestUserAPI:
    @classmethod
    def setup_class(cls):
        cls.base_url = "/users/{}/follow"
        cls.expected_response = {"result": True}
        cls.error_response = {
            "result": False,
            "error_type": "Bad Request",
            "error_message": "",
        }

    @pytest.mark.asyncio
    async def test_follow_user_correct(self, client: AsyncClient):
        if hasattr(self, "base_url"):
            response = await client.post(self.base_url.format("5"))
            assert response.status_code == 200
            if hasattr(self, "expected_response"):
                assert response.json() == self.expected_response
                assert MSG(**response.json())

    @pytest.mark.asyncio
    async def test_follow_yourself(self, client: AsyncClient):
        if hasattr(self, "error_response") and hasattr(self, "base_url"):
            self.error_response["error_message"] = "Нельзя подписаться на самого себя"
            response = await client.post(self.base_url.format("1"))
            assert response.status_code == 400
            assert response.json() == self.error_response
            assert ErrorMSG(**response.json())

    @pytest.mark.asyncio
    async def test_follow_user_that_doesnt_exist(self, client: AsyncClient):
        if hasattr(self, "error_response") and hasattr(self, "base_url"):
            self.error_response["error_type"] = "Not Found"
            self.error_response["error_message"] = "Пользователь не найден"
            response = await client.post(self.base_url.format("10000"))
            assert response.status_code == 404
            assert response.json() == self.error_response
            assert ErrorMSG(**response.json())

    @pytest.mark.asyncio
    async def test_unfollow_user(self, client: AsyncClient):
        if hasattr(self, "expected_response") and hasattr(self, "base_url"):
            url = self.base_url.format("5")
            following_response = await client.post(url)
            assert following_response.status_code == 200
            response = await client.delete(url)
            assert response.status_code == 200
            assert response.json() == self.expected_response
            assert MSG(**response.json())

    @pytest.mark.asyncio
    async def test_unfollow_user_that_is_not_followed(
        self, client: AsyncClient
    ):
        if hasattr(self, "error_response") and hasattr(self, "base_url"):
            self.error_response["error_type"] = "Bad Request"
            self.error_response["error_message"] = (
                "Вы не подписаны на этого пользователя"
            )
            response = await client.delete(self.base_url.format(6))
            assert response.status_code == 400
            assert response.json() == self.error_response
            assert ErrorMSG(**response.json())

    @pytest.mark.asyncio
    async def test_get_user_info(self, client: AsyncClient):
        if hasattr(self, "base_url"):
            url = self.base_url.replace("/follow", "")
            response = await client.get(url.format(1))
            assert response.status_code == 200
            assert GetUser(**response.json())

    @pytest.mark.asyncio
    async def test_get_me_info(self, client: AsyncClient):
        if hasattr(self, "base_url"):
            url = self.base_url.replace("{}/follow", "me")
            response = await client.get(url)
            assert response.status_code == 200
            assert GetUser(**response.json())

    @pytest.mark.asyncio
    @pytest.mark.parametrize("unauthorized", ["/users/me"])
    async def test_get_wrong_auth(
        self, invalid_client: AsyncClient, unauthorized: str
    ):
        response = await invalid_client.get(unauthorized)
        self.error_response["error_message"] = "Неверный API ключ"
        self.error_response["error_type"] = "Unauthorized"
        assert response.status_code == 401
        assert response.json() == self.error_response
        assert ErrorMSG(**response.json())

    @pytest.mark.asyncio
    async def test_post_wrong_auth(self, invalid_client: AsyncClient):
        if hasattr(self, "base_url"):
            response = await invalid_client.post(self.base_url.format("1"))
            self.error_response["error_message"] = "Неверный API ключ"
            self.error_response["error_type"] = "Unauthorized"
            assert response.status_code == 401
            assert response.json() == self.error_response
            assert ErrorMSG(**response.json())
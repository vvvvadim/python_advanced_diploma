import pytest
from httpx import AsyncClient

from tests.conftest import unauthorized_structure_response


class TestTweetAPI:
    @classmethod
    def setup_class(cls):
        cls.text = "random tweet text"
        cls.base_url = "/tweets"
        cls.likes_url = "/tweets/{}/likes"
        cls.tweet_structure = {
            "tweet_data": "",
            "tweet_media_ids": [],
        }
        cls.expected_response = {"result": True}
        cls.tweet_response = {
            "result": True,
            "tweet_id" : int
        }
        cls.error_response = {
            "result": False,
            "error_type": "Bad Request",
            "error_message": "",
        }

    @pytest.mark.asyncio
    async def test_create_tweet(self, client: AsyncClient):
        if (
            hasattr(self, "tweet_structure")
            and hasattr(self, "text")
            and hasattr(self, "base_url")
        ):
            self.tweet_structure["tweet_data"] = self.text
            response = await client.post(
                self.base_url, json=self.tweet_structure
            )
            assert response.status_code == 200
            assert isinstance(response.json()["tweet_id"], int)
            assert response.json()["result"] == True

    @pytest.mark.asyncio
    async def test_delete_tweet(self, client: AsyncClient):
        if (
            hasattr(self, "base_url")
        ):
            response = await client.delete(
                self.base_url+"/1"
            )
            assert response.status_code == 200
            assert response.json() == self.expected_response

    @pytest.mark.asyncio
    async def test_delete_tweet_alien_id(self, client: AsyncClient):
        if (
            hasattr(self, "base_url")
        ):
            response = await client.delete(
                self.base_url+"/2"
            )
            self.error_response["error_message"] = "У вас нет прав на выполнение этой операции"
            self.error_response["error_type"] = "Forbidden"
            assert response.status_code == 403
            assert response.json() == self.error_response

    @pytest.mark.asyncio
    async def test_delete_tweet_wrong_id(self, client: AsyncClient):
        if (
            hasattr(self, "base_url")
        ):
            response = await client.delete(
                self.base_url+"/20000"
            )
            self.error_response["error_message"] = "У вас нет прав на выполнение этой операции"
            self.error_response["error_type"] = "Forbidden"
            assert response.status_code == 403
            assert response.json() == self.error_response

    @pytest.mark.asyncio
    async def test_post_like_tweet(self, client: AsyncClient):
        if (
            hasattr(self, "likes_url")
        ):
            response = await client.post(
                self.likes_url.format("3")
                            )
            assert response.status_code == 200
            assert response.json() == self.expected_response

    @pytest.mark.asyncio
    async def test_delete_like_tweet(self, client: AsyncClient):
        if (
            hasattr(self, "likes_url")
        ):
            response = await client.post(
                self.likes_url.format("3")
                            )
            assert response.status_code == 200
            assert response.json() == self.expected_response

    @pytest.mark.asyncio
    async def test_delete_like_tweet_wrong_id(self, client: AsyncClient):
        if (
            hasattr(self, "likes_url")
        ):
            response = await client.delete(
                self.likes_url.format("3000")
                            )
            self.error_response["error_message"] = "Лайк не найден"
            self.error_response["error_type"] = "Internal Server Error"
            assert response.status_code == 500
            assert response.json() == self.error_response

    @pytest.mark.asyncio
    async def test_post_like_tweet_wrong_id(self, client: AsyncClient):
        if (
            hasattr(self, "likes_url")
        ):
            response = await client.post(
                self.likes_url.format("3000")
                            )
            self.error_response["error_message"] = "Твит не найден"
            self.error_response["error_type"] = "Internal Server Error"
            assert response.status_code == 500
            assert response.json() == self.error_response
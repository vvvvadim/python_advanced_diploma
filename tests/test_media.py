import pytest
from httpx import AsyncClient
from io import BytesIO
from api.config.schemas import PostMedia, ErrorMSG

class TestMediaAPI:
    @classmethod
    def setup_class(cls):
        image = b"Test"
        file_image = BytesIO(image)
        cls.file = {"file" : ("photo.jpg",file_image)}
        cls.wrong_file = {"file" : ("photo.jpg")}
        cls.base_url = "/medias"

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_media_route(self, client: AsyncClient):
        if hasattr(self, "base_url") and hasattr(self, "files"):
            response = await client.post(self.base_url, files=self.files)

            assert response.status_code == 201
            assert response.json()["result"] == True
            assert PostMedia(**response.json())

    @pytest.mark.asyncio
    async def test_incorrect_api_key(self, client: AsyncClient):
        if hasattr(self, "base_url") and hasattr(self, "files"):
            headers = {"api-key": "RMTREE"}
            response = await client.post(
                self.base_url, headers=headers, files=self.files
            )
            assert response.status_code == 401
            assert response.json()["result"] == False
            assert ErrorMSG(**response.json())
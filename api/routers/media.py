from fastapi import UploadFile, status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import os
import aiofiles
import uuid
from api.config.config import MEDIA_FOLDER
from api.database.database import get_async_session
from api.function.media_func import post_media

media_router = APIRouter(tags=["Работа с медиаданными"])

@media_router.post("/api/medias",
                   status_code=status.HTTP_200_OK,
                   response_model=None,
                   name="Загрузка медиа данных",
                   description="Загрузка медиа данных")
async def upload_file(
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session)
):
    file_id = (str(uuid.uuid4())
               + '.'
               + '.'.join(file.filename.split('.')[-1:]))
    file.filename = file_id
    contents = await file.read()
    path1 = os.path.join(MEDIA_FOLDER, file.filename)
    async with aiofiles.open(path1, mode='wb') as f:
        await f.write(contents)
        await file.close()
    return await post_media(file=file.filename, session=session)

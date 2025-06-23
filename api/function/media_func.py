from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.config.config import logger
from api.config.models import Media


async def post_media(file: str, session: AsyncSession) -> Dict:
    """Сохранение медиафайла"""
    try:
        # Создаем запись в базе данных
        logger.info("Начата попытка записи данных о загруженном файле в БД")
        media = Media(link=file)
        session.add(media)
        await session.flush()

        return {"result": "true", "media_id": media.id}

    except Exception as e:
        logger.error("Ошибка при сохранении файла")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении файла: {str(e)}",
        )

from fastapi import APIRouter, Depends
from database.models import Contact
from database.engine import get_session

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


stats_router = APIRouter(prefix="/stats", tags=["Статистика"])


@stats_router.get("/distribution")
async def get_distribution_stats(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(
            Contact.operator_id,
            Contact.source_id,
            func.count(Contact.id).label("count"),
        ).group_by(Contact.operator_id, Contact.source_id)
    )

    stats = result.all()

    return [
        {
            "operator_id": s.operator_id,
            "source_id": s.source_id,
            "contacts_count": s.count,
        }
        for s in stats
    ]

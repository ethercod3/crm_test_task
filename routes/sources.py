from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, HTTPException

from database.models import Operator, Source, SourceOperatorWeight
from database.engine import get_session

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from schemas import SourceCreate, SourceWeightConfig


sources_router = APIRouter(prefix="/sources", tags=["Источники"])


@sources_router.post("/")
async def create_source(
    source: SourceCreate, session: AsyncSession = Depends(get_session)
):
    db_source = Source(name=source.name)
    session.add(db_source)
    await session.commit()
    await session.refresh(db_source)
    return {"id": db_source.id, "name": db_source.name}


@sources_router.get("/")
async def list_sources(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Source))
    sources = result.scalars().all()
    return [{"id": s.id, "name": s.name} for s in sources]


@sources_router.post("/weights")
async def configure_source_weights(
    config: SourceWeightConfig, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Source).where(Source.id == config.source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    await session.execute(
        select(SourceOperatorWeight).where(
            SourceOperatorWeight.source_id == config.source_id
        )
    )
    existing = (
        (
            await session.execute(
                select(SourceOperatorWeight).where(
                    SourceOperatorWeight.source_id == config.source_id
                )
            )
        )
        .scalars()
        .all()
    )

    for weight in existing:
        await session.delete(weight)

    for w in config.weights:
        op_result = await session.execute(
            select(Operator).where(Operator.id == w.operator_id)
        )
        if not op_result.scalar_one_or_none():
            raise HTTPException(
                status_code=404, detail=f"Operator {w.operator_id} not found"
            )

        db_weight = SourceOperatorWeight(
            source_id=config.source_id, operator_id=w.operator_id, weight=w.weight
        )
        session.add(db_weight)

    await session.commit()
    return {"message": "Weights configured successfully"}


@sources_router.get("/{source_id}/weights")
async def get_source_weights(
    source_id: int, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(SourceOperatorWeight)
        .options(selectinload(SourceOperatorWeight.operator))
        .where(SourceOperatorWeight.source_id == source_id)
    )
    weights = result.scalars().all()

    return [
        {
            "operator_id": w.operator_id,
            "weight": w.weight,
            "operator_name": w.operator.name,
        }
        for w in weights
    ]

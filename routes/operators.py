from fastapi import APIRouter, Depends, HTTPException

from database.models import Operator, Contact
from database.engine import get_session

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


from schemas import (
    OperatorCreate,
    OperatorUpdate,
    OperatorResponse,
)


operators_router = APIRouter(prefix="/operators", tags=["Операторы"])


@operators_router.post("/", response_model=dict)
async def create_operator(
    operator: OperatorCreate, session: AsyncSession = Depends(get_session)
):
    db_operator = Operator(
        name=operator.name, active=operator.active, load_limit=operator.load_limit
    )
    session.add(db_operator)
    await session.commit()
    await session.refresh(db_operator)
    return {"id": db_operator.id, "name": db_operator.name}


@operators_router.get("/", response_model=list[OperatorResponse])
async def list_operators(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Operator))
    operators = result.scalars().all()

    response = []
    for op in operators:
        count_result = await session.execute(
            select(func.count(Contact.id)).where(
                Contact.operator_id == op.id, Contact.status == "active"
            )
        )
        current_load = count_result.scalar()
        response.append(
            OperatorResponse(
                id=op.id,
                name=op.name,
                active=op.active,
                load_limit=op.load_limit,
                current_load=current_load,
            )
        )

    return response


@operators_router.patch("/{operator_id}")
async def update_operator(
    operator_id: int,
    operator_update: OperatorUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Operator).where(Operator.id == operator_id))
    operator = result.scalar_one_or_none()

    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")

    if operator_update.active is not None:
        operator.active = operator_update.active
    if operator_update.load_limit is not None:
        operator.load_limit = operator_update.load_limit

    await session.commit()
    return {
        "id": operator.id,
        "active": operator.active,
        "load_limit": operator.load_limit,
    }

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from database.models import Lead, Contact, SourceOperatorWeight, Source, Operator
from sqlalchemy.ext.asyncio import AsyncSession
import random


class LeadService:
    @staticmethod
    async def get_or_create_lead(
        session: AsyncSession, external_id: str, name: str | None = None
    ):
        result = await session.execute(
            select(Lead).where(Lead.external_id == external_id)
        )
        lead = result.scalar_one_or_none()
        if lead:
            return lead
        lead = Lead(external_id=external_id, name=name)
        session.add(lead)
        await session.flush()
        return lead


class OperatorService:
    @staticmethod
    async def get_available_operators(session: AsyncSession, source_id: int):
        result = await session.execute(
            select(SourceOperatorWeight)
            .options(selectinload(SourceOperatorWeight.operator))
            .where(SourceOperatorWeight.source_id == source_id)
        )
        weights = result.scalars().all()

        available = []
        for w in weights:
            op = w.operator

            if not op.active:
                continue

            count_result = await session.execute(
                select(func.count(Contact.id)).where(
                    Contact.operator_id == op.id, Contact.status == "active"
                )
            )
            active_count = count_result.scalar()

            if active_count < op.load_limit:
                available.append((op, w.weight))

        return available

    @staticmethod
    def pick_operator_weighted(
        available: list[tuple[Operator, int]],
    ) -> Operator | None:
        if not available:
            return None

        operators = [op for op, _ in available]
        weights = [w for _, w in available]

        return random.choices(operators, weights=weights, k=1)[0]


class ContactService:
    @staticmethod
    async def create_contact(
        session: AsyncSession, lead: Lead, source: Source
    ) -> Contact:
        available = await OperatorService.get_available_operators(session, source.id)
        operator = OperatorService.pick_operator_weighted(available)

        contact = Contact(
            lead_id=lead.id,
            source_id=source.id,
            operator_id=operator.id if operator else None,
            status="active",
        )
        session.add(contact)
        await session.flush()
        return contact

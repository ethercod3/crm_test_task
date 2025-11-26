from fastapi import APIRouter, Depends, HTTPException

from database.models import Lead, Contact
from database.engine import get_session

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func


from schemas import LeadResponse


leads_router = APIRouter(prefix="/leads", tags=["Лиды"])


@leads_router.get("/", response_model=list[LeadResponse])
async def list_leads(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Lead))
    leads = result.scalars().all()

    response = []
    for lead in leads:
        count_result = await session.execute(
            select(func.count(Contact.id)).where(Contact.lead_id == lead.id)
        )
        contacts_count = count_result.scalar()
        response.append(
            LeadResponse(
                id=lead.id,
                external_id=lead.external_id,
                name=lead.name,
                contacts_count=contacts_count,
            )
        )

    return response


@leads_router.get("/{lead_id}/contacts")
async def get_lead_contacts(lead_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    contacts_result = await session.execute(
        select(Contact).where(Contact.lead_id == lead_id)
    )
    contacts = contacts_result.scalars().all()

    return {
        "lead": {"id": lead.id, "external_id": lead.external_id, "name": lead.name},
        "contacts": [
            {
                "id": c.id,
                "source_id": c.source_id,
                "operator_id": c.operator_id,
                "status": c.status,
            }
            for c in contacts
        ],
    }

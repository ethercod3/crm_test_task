from fastapi import APIRouter, Depends, HTTPException

from database.models import Contact, Source
from database.engine import get_session
from services.services import LeadService, ContactService

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from schemas import ContactResponse, ContactCreate


contacts_router = APIRouter(prefix="/contacts", tags=["Контакты"])


@contacts_router.post("/", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate, session: AsyncSession = Depends(get_session)
):
    source_result = await session.execute(
        select(Source).where(Source.id == contact_data.source_id)
    )
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    lead = await LeadService.get_or_create_lead(
        session, contact_data.lead_external_id, contact_data.lead_name
    )

    contact = await ContactService.create_contact(session, lead, source)

    await session.commit()
    await session.refresh(contact)

    return ContactResponse(
        id=contact.id,
        lead_id=contact.lead_id,
        source_id=contact.source_id,
        operator_id=contact.operator_id,
        status=contact.status,
    )


@contacts_router.get("/")
async def list_contacts(limit: int = 50, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Contact).limit(limit).order_by(Contact.id.desc())
    )
    contacts = result.scalars().all()

    return [
        {
            "id": c.id,
            "lead_id": c.lead_id,
            "source_id": c.source_id,
            "operator_id": c.operator_id,
            "status": c.status,
        }
        for c in contacts
    ]


@contacts_router.patch("/{contact_id}/close")
async def close_contact(contact_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.status = "closed"
    await session.commit()
    return {"id": contact.id, "status": contact.status}

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    load_limit = Column(Integer, default=10)

    contacts = relationship("Contact", back_populates="operator")
    weights = relationship("SourceOperatorWeight", back_populates="operator")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    external_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)

    contacts = relationship("Contact", back_populates="lead")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    weights = relationship("SourceOperatorWeight", back_populates="source")
    contacts = relationship("Contact", back_populates="source")


class SourceOperatorWeight(Base):
    __tablename__ = "source_operator_weights"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"))
    weight = Column(Integer, default=1)

    source = relationship("Source", back_populates="weights")
    operator = relationship("Operator", back_populates="weights")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(String, default="active")

    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=5)

    # Связь с назначениями по источникам
    source_assignments = relationship("SourceOperator", back_populates="operator")
    tickets = relationship("Ticket", back_populates="operator")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # внешний ID для идентификации
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="lead")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # название бота/источника

    # Связь с назначениями операторов
    operator_assignments = relationship("SourceOperator", back_populates="source")
    tickets = relationship("Ticket", back_populates="source")


class SourceOperator(Base):
    __tablename__ = "source_operators"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"))
    weight = Column(Integer, default=10)  # вес оператора для этого источника

    source = relationship("Source", back_populates="operator_assignments")
    operator = relationship("Operator", back_populates="source_assignments")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="new")  # new, in_progress, closed

    lead = relationship("Lead", back_populates="tickets")
    source = relationship("Source", back_populates="tickets")
    operator = relationship("Operator", back_populates="tickets")
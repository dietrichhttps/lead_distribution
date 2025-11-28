from fastapi import FastAPI, HTTPException, Depends
from pydantic import model_validator
from sqlalchemy.orm import Session
from typing import List

from app.models.models import Operator, Source, SourceOperator, Ticket, Lead
from app.schemas.lead import LeadResponse
from app.schemas.operator import OperatorResponse, OperatorBase
from app.schemas.source import SourceResponse, SourceBase, SourceOperatorAssignment
from app.schemas.ticket import TicketResponse, TicketCreate
from app.services.distribution import get_db, DistributionService

app = FastAPI(title="Lead Distribution CRM", version="1.0.0")


# ==================== API ЭНДПОИНТЫ ====================
@app.post("/operators/", response_model=OperatorResponse)
def create_operator(operator: OperatorBase, db: Session = Depends(get_db)):
    db_operator = Operator(**operator.dict())
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator

@app.get("/operators/", response_model=List[OperatorResponse])
def list_operators(db: Session = Depends(get_db)):
    operators = db.query(Operator).all()
    result = []
    for op in operators:
        op_data = OperatorResponse.model_validate(op)
        op_data.current_load = DistributionService.get_operator_current_load(db, op.id)
        result.append(op_data)
    return result


@app.post("/sources/", response_model=SourceResponse)
def create_source(source: SourceBase, db: Session = Depends(get_db)):
    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@app.post("/sources/{source_id}/assign-operators/")
def assign_operators_to_source(
        source_id: int,
        assignments: List[SourceOperatorAssignment],
        db: Session = Depends(get_db)
):
    # Удаляем старые назначения
    db.query(SourceOperator).filter(SourceOperator.source_id == source_id).delete()

    # Добавляем новые
    for assignment in assignments:
        db_assignment = SourceOperator(
            source_id=source_id,
            operator_id=assignment.operator_id,
            weight=assignment.weight
        )
        db.add(db_assignment)

    db.commit()
    return {"message": "Operators assigned successfully"}


@app.post("/tickets/", response_model=TicketResponse)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    # 1. Найти или создать лида
    lead = DistributionService.find_or_create_lead(
        db, ticket_data.lead_external_id, ticket_data.phone, ticket_data.email
    )

    # 2. Проверить существование источника
    source = db.query(Source).filter(Source.id == ticket_data.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # 3. Назначить оператора
    operator = DistributionService.assign_ticket(db, ticket_data.source_id)

    # 4. Создать обращение
    ticket = Ticket(
        lead_id=lead.id,
        source_id=ticket_data.source_id,
        operator_id=operator.id if operator else None,
        status="new"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Формируем ответ
    response = TicketResponse(
        id=ticket.id,
        lead_id=ticket.lead_id,
        source_id=ticket.source_id,
        operator_id=ticket.operator_id,
        created_at=ticket.created_at,
        status=ticket.status,
        lead=LeadResponse.model_validate(lead),
        source=SourceResponse.model_validate(source),
        operator=OperatorResponse.model_validate(operator) if operator else None
    )

    return response


@app.get("/tickets/", response_model=List[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return tickets


@app.get("/leads/", response_model=List[LeadResponse])
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    result = []
    for lead in leads:
        lead_data = LeadResponse.model_validate(lead)
        lead_data.tickets_count = len(lead.tickets)
        result.append(lead_data)
    return result
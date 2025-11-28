import random
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.models import Lead, Ticket, SourceOperator, Operator


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DistributionService:
    @staticmethod
    def find_or_create_lead(db: Session, external_id: str, phone: str = None, email: str = None) -> Lead:
        """Найти или создать лида по external_id"""
        lead = db.query(Lead).filter(Lead.external_id == external_id).first()
        if not lead:
            lead = Lead(external_id=external_id, phone=phone, email=email)
            db.add(lead)
            db.commit()
            db.refresh(lead)
        return lead

    @staticmethod
    def get_operator_current_load(db: Session, operator_id: int) -> int:
        """Получить текущую нагрузку оператора (кол-во активных обращений)"""
        return db.query(Ticket).filter(
            Ticket.operator_id == operator_id,
            Ticket.status.in_(["new", "in_progress"])
        ).count()

    @staticmethod
    def find_available_operators(db: Session, source_id: int) -> List[dict]:
        """Найти доступных операторов для источника с учетом нагрузки"""
        # Получаем всех операторов, назначенных на этот источник
        assignments = db.query(SourceOperator).filter(
            SourceOperator.source_id == source_id
        ).all()

        available_operators = []
        total_weight = 0

        for assignment in assignments:
            operator = assignment.operator

            # Проверяем активность и нагрузку
            if operator.is_active:
                current_load = DistributionService.get_operator_current_load(db, operator.id)
                if current_load < operator.max_load:
                    available_operators.append({
                        'operator': operator,
                        'weight': assignment.weight
                    })
                    total_weight += assignment.weight

        return available_operators, total_weight

    @staticmethod
    def select_operator(available_operators: List[dict], total_weight: int) -> Optional[Operator]:
        """Выбрать оператора по весам"""
        if not available_operators:
            return None

        if total_weight == 0:
            return available_operators[0]['operator']

        # Случайный выбор с учетом весов
        rand = random.randint(1, total_weight)
        current = 0

        for item in available_operators:
            current += item['weight']
            if rand <= current:
                return item['operator']

        return available_operators[0]['operator']  # fallback

    @staticmethod
    def assign_ticket(db: Session, source_id: int) -> Optional[Operator]:
        """Основная логика распределения обращения"""
        available_operators, total_weight = DistributionService.find_available_operators(db, source_id)
        return DistributionService.select_operator(available_operators, total_weight)
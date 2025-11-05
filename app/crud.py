from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models


def get_all_terms(db: Session) -> Sequence[models.Term]:
    stmt = select(models.Term).order_by(models.Term.term.asc())
    return db.execute(stmt).scalars().all()


def get_term_by_name(db: Session, term: str) -> Optional[models.Term]:
    stmt = select(models.Term).where(models.Term.term == term)
    return db.execute(stmt).scalar_one_or_none()


def create_term(db: Session, term: str, description: str) -> models.Term:
    new_term = models.Term(term=term, description=description)
    db.add(new_term)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(new_term)
    return new_term


def update_term_description(db: Session, term: str, description: str) -> Optional[models.Term]:
    existing = get_term_by_name(db, term)
    if existing is None:
        return None
    existing.description = description
    db.commit()
    db.refresh(existing)
    return existing


def delete_term(db: Session, term: str) -> bool:
    existing = get_term_by_name(db, term)
    if existing is None:
        return False
    db.delete(existing)
    db.commit()
    return True

